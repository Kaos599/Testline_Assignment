# Personalized Student Performance Recommendations for NEET Testline 🚀

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![Google Gemini API](https://img.shields.io/badge/Google_Gemini_API-Powered-orange.svg?style=flat-square&logo=google-gemini&logoColor=white)](https://ai.google.dev/gemini-api)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project is my solution to provide personalized study recommendations for students using the NEET Testline app. I've built a Python script that analyzes quiz performance data and leverages the power of Google's Gemini AI to deliver actionable insights and recommendations, helping students focus their preparation effectively.

## Data Overview

I worked with two main datasets to perform this analysis:

*   **Current Quiz Data:** This dataset provides details about a user's most recent quiz submission. It includes information like:
    *   Quiz ID and details (topic, difficulty level, etc.)
    *   User ID
    *   Submission timestamps
    *   Score, accuracy, speed, and other performance metrics
    *   A `response_map` linking Question IDs to the selected option IDs.

*   **Historical Quiz Data:** This dataset contains performance data from the last 5 quizzes for each user. It includes:
    *   Quiz IDs and details
    *   User IDs
    *   Submission timestamps
    *   Scores, accuracy, speed, and performance metrics for each quiz
    *   `response_map` for each historical quiz.

These datasets are provided via API endpoints.

## Task

The core tasks I tackled in this project were:

*   **Analyze the Data:** I explored the schema of both datasets to understand the available information. Then, I focused on identifying patterns in student performance across:
    *   Topics
    *   Difficulty Levels (if available, currently data has `difficulty_level: null`)
    *   Response Accuracy

*   **Generate Insights:**  Based on the analysis, I aimed to highlight key insights for each student, including:
    *   **Weak Areas:**  Identify topics where the student consistently underperforms.
    *   **Improvement Trends:**  Determine if the student is showing progress over their last few quizzes.
    *   **Performance Gaps:**  Pinpoint the difference in performance between strong and weak areas.
    *   **Speed vs. Accuracy Analysis:** Analyze if the student's quiz completion speed is impacting their accuracy.
    *   **Difficulty Level Recommendation:** Suggest appropriate quiz difficulty levels for weak topics.
    *   **Mistake Pattern (Basic):** Count total incorrect answers per topic to find areas of frequent mistakes.

*   **Create Recommendations:** The ultimate goal was to generate personalized and actionable recommendations for students to improve. These recommendations include:
    *   Suggested topics to focus on.
    *   Recommended quiz difficulty levels for practice.
    *   Tips on time management during quizzes (based on speed analysis).
    *   General study advice.
    *   Specific study actions for weak topics.

*   **Bonus Points:**  To add extra value, I also aimed to:
    *   **Define a Student Persona:** Based on performance patterns, assign a creative persona label to characterize the student's learning style.
    *   **Highlight Strengths and Weaknesses with Creative Labels:**  Use engaging labels to describe the student's strong and weak areas.

## Implemented Features 💪

Here's what I've built into this Python script:

*   **Data Fetching:** I implemented functions to dynamically fetch quiz data from the provided API endpoints using the `requests` library. Error handling is included to manage potential issues with fetching data.
*   **Topic-wise Performance Analysis:**  The script calculates average accuracy, score, and quiz duration for each topic based on historical data, allowing for easy identification of strong and weak areas.
*   **Performance Trend Analysis:**  I analyze the accuracy and score trends from the last few quizzes to provide insights into the student's progress over time.
*   **Difficulty Level Recommendations:**  Based on average accuracy in weak topics, the script suggests starting with "Easy," "Medium," or "Normal" difficulty quizzes for focused practice.
*   **Speed vs. Accuracy Analysis:**  The script analyzes the time spent per question in the latest quiz and compares it to accuracy. It identifies if a student might be rushing and suggests adjusting their pace.
*   **Basic Mistake Pattern Analysis:** I calculate and display the total number of incorrect answers per topic from historical quizzes to highlight areas with frequent mistakes.
*   **Google Gemini AI Integration:**  I've integrated Google's Gemini API to generate more human-readable and personalized feedback and study recommendations. The prompt is designed to request structured JSON output for easy parsing and display. The feedback incorporates insights from all the analyses performed.
*   **Structured JSON Output:**  The GenAI output is parsed as JSON, providing structured data for feedback, topic-specific recommendations (with actions), and general recommendations. This makes it easy to use the output in an application.
*   **Text-Based Fallback:** The script also includes text-based outputs for all analyses and recommendations, serving as a fallback if the GenAI integration has issues or for comparison.
*   **Linting and Documentation:** The code is formatted and documented for better readability and maintainability, following Python best practices.

## Setup Instructions ⚙️

To run this script, you'll need to:

1.  **Python Environment:** Ensure you have Python 3.9 or later installed.
2.  **Install Libraries:** Install the required Python libraries using pip:
    ```bash
    pip install requests google-generativeai
    ```
3.  **Set Gemini API Key:** Obtain a Google Gemini API key from [Google AI Studio](https://aistudio.google.com/) and set it as an environment variable named `GEMINI_API_KEY`.  For example, in your terminal:
    ```bash
    export GEMINI_API_KEY=YOUR_ACTUAL_GEMINI_API_KEY
    ```
4.  **Run the Script:** Execute the Python script from your terminal:
    ```bash
    python main.py
    ```

## Project Overview and Approach Description 🗺️

This project aims to empower students using the NEET Testline app with data-driven, personalized guidance.  My approach is centered around these key steps:

1.  **Data Acquisition:** I start by fetching the necessary quiz data from the provided API endpoints, ensuring robust error handling in case of network issues.
2.  **Data Processing and Analysis:**  The core of the script involves processing the historical quiz data to calculate key performance indicators. This includes:
    *   Calculating accuracy, score, and quiz duration for each quiz and topic.
    *   Identifying strongest and weakest topics based on average accuracy.
    *   Analyzing performance trends over the last quizzes.
    *   Performing speed vs. accuracy analysis on the latest quiz.
    *   Recommending difficulty levels for weak topics.
    *   Counting incorrect answers per topic.
3.  **Insight Generation:**  The analysis results are then translated into actionable insights, highlighting weak areas, improvement trends, speed concerns, and difficulty level guidance.
4.  **Personalized Recommendation Generation (GenAI):**  I leverage the Google Gemini API to create personalized feedback and study recommendations. The prompt I designed provides Gemini with the analysis results (strong/weak topics, trends, speed insight, difficulty recommendations) and instructions to generate:
    *   Encouraging and constructive overall feedback.
    *   Specific study actions for each weak topic.
    *   General study recommendations.
    *   The output is structured in JSON for easy use in applications.
5.  **Output Display:**  The script prints the analysis results, insights, and both the text-based and GenAI-powered recommendations to the console. The JSON output from GenAI is also displayed in a formatted manner.

My approach focuses on combining quantitative data analysis with the natural language generation capabilities of GenAI/NLP to create a truly personalized and helpful learning experience for students.

## Bonus Points - Student Persona and Creative Labels 🌟

As a bonus, I have included:

*   **Student Persona:** Based on the observed performance patterns (currently a basic "Inconsistent Achiever" persona), the script assigns a descriptive persona label. This can be further refined with more sophisticated analysis and potentially ML clustering in the future.
*   **Creative Labels for Strengths and Weaknesses:**  The script dynamically generates creative and engaging labels for the student's strongest and weakest topic areas, making the feedback more engaging and less dry.
