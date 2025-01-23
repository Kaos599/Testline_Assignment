import json
import requests
from requests.exceptions import RequestException  
import os  
import google.generativeai as genai  


quiz_endpoint_url = "https://www.jsonkeeper.com/b/LLQT"        
current_quiz_submission_url = "https://api.jsonserve.com/rJvd7g" 
historical_quiz_data_url = "https://api.jsonserve.com/XgAgFJ"      


def fetch_json_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  
        return response.json()
    except RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None  


quiz_endpoint_data = fetch_json_from_url(quiz_endpoint_url)
current_quiz_submission_data = fetch_json_from_url(current_quiz_submission_url)
historical_quiz_data = fetch_json_from_url(historical_quiz_data_url)



if historical_quiz_data is None or current_quiz_submission_data is None or quiz_endpoint_data is None:
    print("Failed to retrieve data from one or more endpoints. Exiting.")
    exit()  


topic_performance = {}
performance_history = []

for quiz_data in historical_quiz_data:  
    topic = quiz_data['quiz']['topic'].strip()
    accuracy = float(quiz_data['accuracy'].replace('%', '').strip())
    
    score = float(quiz_data['final_score'])
    correct_answers = quiz_data['correct_answers']
    incorrect_answers = quiz_data['incorrect_answers']
    submitted_at = quiz_data['submitted_at']

    performance_history.append({
        'submitted_at': submitted_at,
        'accuracy': accuracy,
        'score': score,
        'topic': topic
    })

    if topic not in topic_performance:
        topic_performance[topic] = {
            'total_accuracy': 0,
            'count': 0,
            'avg_accuracy': 0,
            'highest_accuracy': 0,
            'lowest_accuracy': 100,
            'total_score': 0.0,  
            'avg_score': 0
        }
    topic_performance[topic]['total_accuracy'] += accuracy
    topic_performance[topic]['count'] += 1
    topic_performance[topic]['total_score'] += score  
    topic_performance[topic]['highest_accuracy'] = max(topic_performance[topic]['highest_accuracy'], accuracy)
    topic_performance[topic]['lowest_accuracy'] = min(topic_performance[topic]['lowest_accuracy'], accuracy)

for topic in topic_performance:
    topic_performance[topic]['avg_accuracy'] = topic_performance[topic]['total_accuracy'] / topic_performance[topic]['count']
    topic_performance[topic]['avg_score'] = topic_performance[topic]['total_score'] / topic_performance[topic]['count']

sorted_topic_performance_weakest = sorted(topic_performance.items(), key=lambda item: item[1]['avg_accuracy'])
sorted_topic_performance_strongest = sorted(topic_performance.items(), key=lambda item: item[1]['avg_accuracy'], reverse=True)

performance_history.sort(key=lambda item: item['submitted_at'])

accuracy_trend = [p['accuracy'] for p in performance_history]
score_trend = [p['score'] for p in performance_history]

weak_areas = [topic for topic, perf in sorted_topic_performance_weakest[:3]]
strong_areas = [topic for topic, perf in sorted_topic_performance_strongest[:3]]
improvement_trend_insight = "Mixed trends. Accuracy and score are fluctuating. Needs consistent improvement focus."
if len(accuracy_trend) > 1:
    if accuracy_trend[-1] > accuracy_trend[0]:
        improvement_trend_insight = "Showing improvement in recent quizzes compared to older ones."
    else:
        improvement_trend_insight = "Performance is fluctuating, not showing consistent improvement."




genai.configure(api_key=os.environ["AIzaSyBQBlRTuwDXVmVEj0hJ4ErV4J6wP9ei860"])


generation_config = {
    "temperature": 0.9,  
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",  
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",  
    generation_config=generation_config,
)

chat_session = model.start_chat(history=[])


prompt_gen_ai = f"""
Generate personalized feedback and specific study recommendations for a student based on their quiz performance.

**Student's Strengths (Topics):** {', '.join(strong_areas)}
**Student's Weaknesses (Topics):** {', '.join(weak_areas)}
**Performance Trend:** {improvement_trend_insight}

**Instructions for Response:**

1.  Provide overall encouraging and constructive feedback in a paragraph format.
2.  For each of the Weakness Topics, suggest 2-3 specific and actionable study steps.
3.  Include 2-3 general study recommendations applicable to all topics.
4.  Structure your entire response as a JSON object with the following keys:
    -   "feedback":  (string) Overall feedback paragraph
    -   "recommendations": (array of objects) - Each object represents a weak topic with "topic" (string - topic name) and "actions" (array of strings - study actions) keys.
    -   "general_recommendations": (array of strings) - General study recommendations.

**Example JSON Response Structure:**
```json
{{
  "feedback": "...",
  "recommendations": [
    {{
      "topic": "Weak Topic 1 Name",
      "actions": ["Action 1", "Action 2", ...]
    }},
    {{
      "topic": "Weak Topic 2 Name",
      "actions": ["Action 1", "Action 2", ...]
    }},
    // ... more weak topics as needed
  ],
  "general_recommendations": ["General recommendation 1", "General recommendation 2", ...]
}}
Use code with caution.
Python
"""

response_gen_ai = chat_session.send_message(prompt_gen_ai)

try:
    gen_ai_json_response = json.loads(response_gen_ai.text)  
    feedback_text = gen_ai_json_response.get("feedback", "No feedback generated.")
    topic_recommendations = gen_ai_json_response.get("recommendations", [])
    general_recommendations = gen_ai_json_response.get("general_recommendations", [])

    print("\n--- Gen AI Feedback (Structured JSON) ---")
    print(f"Feedback: {feedback_text}\n")

    if topic_recommendations:
        print("Topic-Specific Recommendations:")
        for rec in topic_recommendations:
            topic_name = rec.get("topic", "N/A")
            actions = rec.get("actions", [])
            print(f"  - **{topic_name}**:")
            for action in actions:
                print(f"    - {action}")
        print()  

    if general_recommendations:
        print("General Study Recommendations:")
        for i, gen_rec in enumerate(general_recommendations, 1):
            print(f"  {i}. {gen_rec}")

except json.JSONDecodeError:
    print("\n--- Gen AI Feedback Error ---")
    print("Could not decode JSON response from Gen AI. Displaying raw text response:")
    print(response_gen_ai.text)  


print("\n--- Analysis of Student Performance (Text-Based - Fallback) ---")
print("\nTopic-wise Performance:")
for topic, perf in sorted_topic_performance_weakest:
    print(f"- Topic: {topic}")
    print(f" Average Accuracy: {perf['avg_accuracy']:.2f}%")
    print(f" Average Score: {perf['avg_score']:.2f}")
    print(f" Highest Accuracy: {perf['highest_accuracy']:.2f}%")
    print(f" Lowest Accuracy: {perf['lowest_accuracy']:.