"""
This script analyzes student quiz performance data fetched from web endpoints.

It retrieves historical quiz data, current quiz submission data, and quiz endpoint details.
The script then performs analysis to identify strong and weak topics, performance trends,
difficulty level recommendations, and speed vs. accuracy insights.

Finally, it uses Google's Gemini AI API to generate personalized feedback and study
recommendations in a structured JSON format, incorporating the analysis results.
The script also provides text-based fallback outputs for insights and recommendations.
"""

import json
import requests
from requests.exceptions import RequestException
import os
from dotenv import load_dotenv
import google.generativeai as genai
import datetime

# --- URLs for endpoints ---
quiz_endpoint_url = "https://www.jsonkeeper.com/b/LLQT"        
current_quiz_submission_url = "https://api.jsonserve.com/rJvd7g" 
historical_quiz_data_url = "https://api.jsonserve.com/XgAgFJ"   

# --- Load Environment Variables ---
load_dotenv()

def fetch_json_from_url(url: str) -> dict or list or None:
    """
    Fetches JSON data from a given URL.

    Args:
        url: The URL to fetch JSON data from.

    Returns:
        A dictionary or list representing the parsed JSON data if successful,
        None if there is an error during the fetching process.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  
        return response.json()
    except RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None


# --- Fetch Data from URLs ---
quiz_endpoint_data = fetch_json_from_url(quiz_endpoint_url)
current_quiz_submission_data = fetch_json_from_url(current_quiz_submission_url)
historical_quiz_data = fetch_json_from_url(historical_quiz_data_url)

# --- Data Validation ---
if historical_quiz_data is None or current_quiz_submission_data is None or quiz_endpoint_data is None:
    print("Failed to retrieve data from one or more endpoints. Exiting.")
    exit()

# --- Analysis Data and Generate Insights ---
topic_performance = {}
performance_history = []
topic_incorrect_counts = {}

for quiz_data in historical_quiz_data:
    topic = quiz_data['quiz']['topic'].strip()
    accuracy = float(quiz_data['accuracy'].replace('%', '').strip())
    score = float(quiz_data['final_score'])
    correct_answers = quiz_data['correct_answers']
    incorrect_answers = quiz_data['incorrect_answers']
    submitted_at = quiz_data['submitted_at']

    # --- Time Analysis ---
    started_at_str = quiz_data['started_at']
    ended_at_str = quiz_data['ended_at']
    started_at_datetime = datetime.datetime.fromisoformat(started_at_str.replace('Z', '+00:00'))
    ended_at_datetime = datetime.datetime.fromisoformat(ended_at_str.replace('Z', '+00:00'))
    duration_seconds = (ended_at_datetime - started_at_datetime).total_seconds()

    performance_history.append({
        'submitted_at': submitted_at,
        'accuracy': accuracy,
        'score': score,
        'topic': topic,
        'duration_seconds': duration_seconds
    })

    if topic not in topic_performance:
        topic_performance[topic] = {
            'total_accuracy': 0,
            'count': 0,
            'avg_accuracy': 0,
            'highest_accuracy': 0,
            'lowest_accuracy': 100,
            'total_score': 0.0,
            'avg_score': 0,
            'total_duration_seconds': 0
        }
    topic_performance[topic]['total_accuracy'] += accuracy
    topic_performance[topic]['count'] += 1
    topic_performance[topic]['total_score'] += score
    topic_performance[topic]['total_duration_seconds'] += duration_seconds
    topic_performance[topic]['highest_accuracy'] = max(topic_performance[topic]['highest_accuracy'], accuracy)
    topic_performance[topic]['lowest_accuracy'] = min(topic_performance[topic]['lowest_accuracy'], accuracy)

    if topic not in topic_incorrect_counts:
        topic_incorrect_counts[topic] = 0
    topic_incorrect_counts[topic] += incorrect_answers

for topic in topic_performance:
    topic_performance[topic]['avg_accuracy'] = topic_performance[topic]['total_accuracy'] / topic_performance[topic]['count']
    topic_performance[topic]['avg_score'] = topic_performance[topic]['total_score'] / topic_performance[topic]['count']
    topic_performance[topic]['avg_duration_minutes'] = topic_performance[topic]['total_duration_seconds'] / topic_performance[topic]['count'] / 60

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

performance_gaps_insight = "Significant performance variation across topics. Strong in some, weak in others."        

# --- Difficulty Level Recommendations ---
difficulty_recommendations = {}
print("\n--- Difficulty Level Recommendations ---")
for topic in weak_areas:
    avg_accuracy = topic_performance[topic]['avg_accuracy']
    if avg_accuracy < 40:
        difficulty_level_rec = "Easy"
        recommendation_text = f"Start with **Easy** difficulty quizzes for **{topic}** to build foundational understanding."
    elif 40 <= avg_accuracy <= 60:
        difficulty_level_rec = "Medium"
        recommendation_text = f"Practice **Medium** difficulty quizzes for **{topic}** to strengthen your concepts."
    else:
        difficulty_level_rec = "Normal"
        recommendation_text = f"Continue practicing **{topic}** at **Normal** difficulty, focusing on accuracy."

    difficulty_recommendations[topic] = difficulty_level_rec
    print(f"- Topic: {topic} - Recommended Difficulty Level: **{difficulty_level_rec}** - Recommendation: {recommendation_text}")

# --- Speed vs. Accuracy Analysis and Recommendation ---
speed_accuracy_insight = None
current_quiz_accuracy = float(current_quiz_submission_data['accuracy'].replace('%', '').strip())

# --- Time Analysis for Current Quiz ---
current_started_at_str = current_quiz_submission_data['started_at']
current_ended_at_str = current_quiz_submission_data['ended_at']
current_started_at_datetime = datetime.datetime.fromisoformat(current_started_at_str.replace('Z', '+00:00'))
current_ended_at_datetime = datetime.datetime.fromisoformat(current_ended_at_str.replace('Z', '+00:00'))
current_duration_seconds = (current_ended_at_datetime - current_started_at_datetime).total_seconds()
current_total_questions = current_quiz_submission_data['total_questions']
current_time_per_question_seconds = current_duration_seconds / current_total_questions if current_total_questions > 0 else 0
current_time_per_question_minutes = current_time_per_question_seconds / 60

time_per_question_threshold_rush_minutes = 0.20  
if current_time_per_question_minutes < time_per_question_threshold_rush_minutes and current_quiz_accuracy < 60:
    speed_accuracy_insight = f"In your latest quiz, you spent an average of just **{current_time_per_question_minutes:.2f} minutes per question**, completing it quickly, but your accuracy was **{current_quiz_accuracy:.0f}%**. This fast pace might be impacting your accuracy. Consider slowing down slightly to ensure you fully understand each question before answering, especially in topics you find challenging."
else:
    speed_accuracy_insight = f"Your speed and accuracy in the latest quiz seem balanced. You spent approximately **{current_time_per_question_minutes:.2f} minutes per question** with an accuracy of **{current_quiz_accuracy:.0f}%**. Maintain this approach, adjusting your pace based on the complexity of the topic and questions."

print("\n--- Speed vs. Accuracy Analysis ---")
print(speed_accuracy_insight)

print("\n--- Mistake Pattern Analysis (Basic) ---")
for topic in weak_areas:
    if topic in topic_incorrect_counts:
        incorrect_count = topic_incorrect_counts[topic]
        print(f"- Topic: {topic} - Total Incorrect Answers in Past Quizzes: {incorrect_count}")

# --- Gen AI Integration (Gemini) ---
genai.configure(api_key = os.getenv("GEMINI_API_KEY"))

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

# --- Construct GenAI Prompt for JSON Response ---
prompt_gen_ai = f"""
Generate personalized feedback and specific study recommendations for a student based on their quiz performance.

**Student's Strengths (Topics):** {', '.join(strong_areas)}
**Student's Weaknesses (Topics):** {', '.join(weak_areas)}
**Performance Trend:** {improvement_trend_insight}
**Difficulty Level Recommendations (for Weak Topics):** {json.dumps(difficulty_recommendations)}
**Speed vs. Accuracy Insight:** {speed_accuracy_insight}
**Average time spent per question in latest quiz:** {current_time_per_question_minutes:.2f} minutes

**Instructions for Response:**

1.  Provide overall encouraging and constructive feedback in a paragraph format, incorporating insights about speed vs. accuracy, time spent per question, and difficulty level recommendations where relevant.
2.  For each of the Weakness Topics, suggest:
        - 2-3 specific and actionable study steps.
        - Identify 1-2 **potential sub-concepts** within the topic where the student might be struggling (if inferable from the topic name).
        - Suggest 1 type of **practice question** that would be beneficial (e.g., conceptual questions, application-based questions, diagram labeling).
        - Suggest 1 type of **learning resource** that could be helpful (e.g., video lecture, online article, interactive simulation).
3.  Include 2-3 general study recommendations applicable to all topics, potentially addressing time management if the speed vs. accuracy analysis suggests rushing.
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

# --- Insights/Stats ---
print("\n--- Analysis of Student Performance (Text-Based - Fallback) ---")
print("\nTopic-wise Performance:")

for topic, perf in sorted_topic_performance_weakest:
    print(f"- Topic: {topic}")
    print(f" Average Accuracy: {perf['avg_accuracy']:.2f}%")
    print(f" Average Score: {perf['avg_score']:.2f}")
    print(f" Average Duration: {perf['avg_duration_minutes']:.2f} minutes")
    print(f" Highest Accuracy: {perf['highest_accuracy']:.2f}%")
    print(f" Lowest Accuracy: {perf['lowest_accuracy']:.2f}%")
    print("-" * 30)

print("\nStrongest Topics:")
print(", ".join(strong_areas))
print("\nWeakest Topics:")
print(", ".join(weak_areas))
print("\nPerformance Trend (Accuracy):", accuracy_trend)
print("Performance Trend (Score):", score_trend)

print("\n--- Insights (Text-Based - Fallback) ---")
print(f"Weak Areas: {', '.join(weak_areas)}")
print(f"Strong Areas: {', '.join(strong_areas)}")
print(f"Improvement Trend: {improvement_trend_insight}")
print(f"Performance Gaps: {performance_gaps_insight}")

recommendations = [
f"Focus on improving in the weak areas: {', '.join(weak_areas)}.",
f"Revisit the concepts of {', '.join(weak_areas)} topics.",
"Practice more quizzes specifically on the weak topics.",
"Analyze incorrect answers in quizzes to understand mistakes.",
"Maintain consistency in performance across all topics."
]

print("\n--- Recommendations (Text-Based - Fallback) ---")
for i, rec in enumerate(recommendations, 1):
    print(f"{i}. {rec}")

# --- Prepare data for Persona calculation (moved from Visualization section) ---
topics = list(topic_performance.keys())
avg_accuracies = [perf['avg_accuracy'] for perf in topic_performance.values()]    

# --- Bonus Points: Student Persona ---
print("\n--- Bonus Points: Student Persona ---")

overall_avg_accuracy = sum(avg_accuracies) / len(avg_accuracies) if avg_accuracies else 0
performance_gap = 0 # Initialize performance_gap
if sorted_topic_performance_strongest and sorted_topic_performance_weakest:
    best_topic_accuracy = sorted_topic_performance_strongest[0][1]['avg_accuracy']
    worst_topic_accuracy = sorted_topic_performance_weakest[0][1]['avg_accuracy']
    performance_gap = best_topic_accuracy - worst_topic_accuracy


time_per_question_threshold_fast_minutes = 0.25 
time_per_question_threshold_slow_minutes = 0.5  

persona_label = "Inconsistent Achiever" 
strengths_label = ""
weaknesses_label = ""

if overall_avg_accuracy >= 85:
    persona_label = "Master Achiever"
    strengths_label = "Mastery Domains: Excels across a wide range of topics."
    weaknesses_label = "Refinement Areas: Minor areas for improvement to reach complete mastery."
elif current_time_per_question_minutes < time_per_question_threshold_fast_minutes and overall_avg_accuracy >= 60:
    persona_label = "Speed Focused Learner"
    strengths_label = "Swift Solver: Excellent quiz completion speed; excels under time pressure."
    weaknesses_label = "Accuracy Boost Needed: Can enhance scores by focusing on accuracy and careful review."
elif current_time_per_question_minutes > time_per_question_slow_minutes and overall_avg_accuracy >= 80:
    persona_label = "Accuracy Seeker"
    strengths_label = "Precision Pro: Prioritizes accuracy and demonstrates strong conceptual understanding."
    weaknesses_label = "Pace Optimization: Could benefit from slightly increasing speed without sacrificing accuracy."
elif performance_gap >= 40 and overall_avg_accuracy >= 60:
    persona_label = "Topic Varied Performer"
    strengths_label = "Topic Strengths: Demonstrates strong grasp in specific topics like " + ', '.join(strong_areas)
    weaknesses_label = "Topic Gaps: Needs to bridge performance gaps in topics like " + ', '.join(weak_areas)
elif overall_avg_accuracy < 60: 
    persona_label = "Needs Support Learner"
    strengths_label = "Developing Potential: Showing effort and engagement through quiz participation."
    weaknesses_label = "Foundational Focus Required: Needs to strengthen foundational concepts across key topics."
else: 
    persona_label = "Inconsistent Achiever"
    strengths_label = "Variable Strengths: Shows potential in some topics, but performance varies."
    weaknesses_label = "Inconsistent Performance: Needs to stabilize performance across all topics."


print(f"Persona: {persona_label}")
print(f"Strengths Insight: {strengths_label}")
print(f"Weaknesses Insight: {weaknesses_label}")

# --- Visualization Section ---
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

plt.ion()

print("\n--- Generating Visualizations ---")

# 1. Topic-wise Average Accuracy - Bar Chart
topics = list(topic_performance.keys())
avg_accuracies = [perf['avg_accuracy'] for perf in topic_performance.values()]

plt.figure(figsize=(12, 6)) 
sns.barplot(x=topics, y=avg_accuracies, palette="viridis", hue=topics, legend=False)
plt.xlabel("Topics")
plt.ylabel("Average Accuracy (%)")
plt.title("Topic-wise Average Quiz Accuracy")
plt.xticks(rotation=45, ha="right") 
plt.tight_layout() 
plt.savefig("topic_accuracy_bar_chart.png") 
print("Generated: topic_accuracy_bar_chart.png")
# plt.show()  # Uncomment plt.show() if you want to display the plot interactively (for testing, not for script output)
plt.close()


# 2. Accuracy Trend Over Time - Line Chart
accuracy_trend_dates = [datetime.datetime.fromisoformat(p['submitted_at']).strftime('%Y-%m-%d') for p in performance_history] 
accuracy_values = [p['accuracy'] for p in performance_history]

plt.figure(figsize=(10, 5))
plt.plot(accuracy_trend_dates, accuracy_values, marker='o', linestyle='-', color='skyblue') 
plt.xlabel("Quiz Submission Date")
plt.ylabel("Accuracy (%)")
plt.title("Quiz Accuracy Trend Over Time")
plt.xticks(rotation=45, ha="right")
plt.grid(axis='y', linestyle='--') 
plt.tight_layout()
plt.savefig("accuracy_trend_line_chart.png")
print("Generated: accuracy_trend_line_chart.png")
# plt.show()
plt.close()


# 3. Quiz Score Distribution - Histogram
quiz_scores = [p['score'] for p in performance_history]

plt.figure(figsize=(8, 5))
sns.histplot(quiz_scores, bins=10, kde=True, color='lightcoral') #
plt.xlabel("Quiz Score")
plt.ylabel("Frequency")
plt.title("Distribution of Quiz Scores")
plt.tight_layout()
plt.savefig("quiz_score_distribution_histogram.png")
print("Generated: quiz_score_distribution_histogram.png")
plt.close()


# 4. Topic-wise Average Quiz Duration - Bar Chart
topic_durations = [perf['avg_duration_minutes'] for perf in topic_performance.values()]

plt.figure(figsize=(12, 6))
sns.barplot(x=topics, y=topic_durations, palette="mako", hue=topics, legend=False) 
plt.xlabel("Topics")
plt.ylabel("Average Quiz Duration (Minutes)")
plt.title("Topic-wise Average Quiz Duration")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("topic_quiz_duration_bar_chart.png")
print("Generated: topic_quiz_duration_bar_chart.png")
plt.close()


# 5. Combined Bar Chart: Weakest vs. Strongest Topics - (Top 3 of each)
weakest_topics_names = [topic for topic, perf in sorted_topic_performance_weakest[:3]]
weakest_topics_accuracies = [topic_performance[topic]['avg_accuracy'] for topic in weakest_topics_names]
strongest_topics_names = [topic for topic, perf in sorted_topic_performance_strongest[:3]]
strongest_topics_accuracies = [topic_performance[topic]['avg_accuracy'] for topic in strongest_topics_names]

combined_topics_names = weakest_topics_names + strongest_topics_names
combined_topics_accuracies = weakest_topics_accuracies + strongest_topics_accuracies
topic_categories = ['Weakest'] * 3 + ['Strongest'] * 3 

df_combined = pd.DataFrame({ 
    'Topic': combined_topics_names,
    'Average Accuracy': combined_topics_accuracies,
    'Category': topic_categories
})


plt.figure(figsize=(10, 6))
sns.barplot(x='Topic', y='Average Accuracy', hue='Category', data=df_combined, palette=['#f05555', '#44bb44']) 
plt.xlabel("Topics")
plt.ylabel("Average Accuracy (%)")
plt.title("Comparison: Average Accuracy - Weakest vs. Strongest Topics")
plt.xticks(rotation=45, ha="right")
plt.legend(title="Topic Category") 
plt.tight_layout()
plt.savefig("weak_vs_strong_topics_bar_chart.png")
print("Generated: weak_vs_strong_topics_bar_chart.png")
plt.close()


print("--- All Visualizations Generated and Saved as PNG files ---")