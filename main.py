import json
import requests
from requests.exceptions import RequestException  


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


print("--- Analysis of Student Performance ---")
print("\nTopic-wise Performance:")
for topic, perf in sorted_topic_performance_weakest:
    print(f"- Topic: {topic}")
    print(f"  Average Accuracy: {perf['avg_accuracy']:.2f}%")
    print(f"  Average Score: {perf['avg_score']:.2f}")
    print(f"  Highest Accuracy: {perf['highest_accuracy']:.2f}%")
    print(f"  Lowest Accuracy: {perf['lowest_accuracy']:.2f}%")
    print("-" * 30)

print("\nStrongest Topics:")
for topic, perf in sorted_topic_performance_strongest[:3]: 
    print(f"- Topic: {topic} - Avg Accuracy: {perf['avg_accuracy']:.2f}%")

print("\nWeakest Topics:")
for topic, perf in sorted_topic_performance_weakest[:3]: 
    print(f"- Topic: {topic} - Avg Accuracy: {perf['avg_accuracy']:.2f}%")


print("\nPerformance Trend (Accuracy - Last Quizzes):", accuracy_trend)
print("Performance Trend (Score - Last Quizzes):", score_trend)



weak_areas = [topic for topic, perf in sorted_topic_performance_weakest[:3]]
strong_areas = [topic for topic, perf in sorted_topic_performance_strongest[:3]]

improvement_trend_insight = "Mixed trends. Accuracy and score are fluctuating. Needs consistent improvement focus."
if len(accuracy_trend) > 1:
    if accuracy_trend[-1] > accuracy_trend[0]:
        improvement_trend_insight = "Showing improvement in recent quizzes compared to older ones."
    else:
        improvement_trend_insight = "Performance is fluctuating, not showing consistent improvement."

performance_gaps_insight = "Significant performance variation across topics. Strong in some, weak in others."


print("\n--- Insights ---")
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

print("\n--- Recommendations ---")
for i, rec in enumerate(recommendations, 1):
    print(f"{i}. {rec}")




persona_label = "Inconsistent Achiever" 
strengths_label = "Topic Strengths: Excels in topics like " + ', '.join(strong_areas) 
weaknesses_label = "Needs Improvement: Requires focus on " + ', '.join(weak_areas) 


print("\n--- Bonus Points: Student Persona ---")
print(f"Persona: {persona_label}")
print(f"Strengths Insight: {strengths_label}")
print(f"Weaknesses Insight: {weaknesses_label}")