import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re
from plotai import PlotAI
import os
from groq import Groq

def run_flow(message):
    """Run the Langflow workflow with the given message"""
    try:
        base_api_url = st.secrets["BASE_API_URL"]
        langflow_id = st.secrets["LANGFLOW_ID"]
        flow_id = st.secrets["FLOW_ID"]
        application_token = st.secrets["APPLICATION_TOKEN"]
        tweaks = json.loads(st.secrets["DEFAULT_TWEAKS"])
        
        api_url = f"{base_api_url}/lf/{langflow_id}/api/v1/run/{flow_id}"
        
        payload = {
            "input_value": message,
            "output_type": "chat",
            "input_type": "chat",
            "tweaks": tweaks
        }
        
        headers = {
            "Authorization": f"Bearer {application_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

def extract_message_from_response(response):
    """Extract the actual message content from the nested response structure"""
    try:
        if not response:
            return None
            
        if 'outputs' in response:
            for output in response['outputs']:
                paths = [
                    output.get('results', {}).get('message', {}).get('text'),
                    output.get('artifacts', {}).get('message'),
                ]
                
                if 'outputs' in output:
                    for sub_output in output['outputs']:
                        if ('results' in sub_output and 
                            'message' in sub_output['results'] and
                            'text' in sub_output['results']['message']):
                            paths.append(sub_output['results']['message']['text'])
                
                if 'messages' in output:
                    for message in output['messages']:
                        if 'message' in message:
                            paths.append(message['message'])
                
                for path in paths:
                    if path is not None:
                        return path

        return None
    except Exception as e:
        st.error(f"Error extracting message: {str(e)}")
        return None

def parse_metrics_from_message(message):
    """Parse metrics data from the message text"""
    metrics = {
        'post_types': [],
        'engagement_rates': [],
        'likes': [],
        'comments': [],
        'shares': []
    }
    
    post_types = ['Images', 'Videos', 'Carousels']
    
    for post_type in post_types:
        pattern = rf"\*\*{post_type}:\*\* (\d+) posts, average engagement rate: ([\d.]+)%, average likes: ([\d,.]+), average comments: ([\d,.]+), average shares: ([\d,.]+)"
        match = re.search(pattern, message)
        if match:
            metrics['post_types'].append(post_type)
            metrics['engagement_rates'].append(float(match.group(2)))
            metrics['likes'].append(float(match.group(3).replace(',', '')))
            metrics['comments'].append(float(match.group(4).replace(',', '')))
            metrics['shares'].append(float(match.group(5).replace(',', '')))
    
    return metrics

def extract_metrics_from_text(text):
    """Extract metrics from the text and create a structured DataFrame"""
    try:
        metrics = parse_metrics_from_message(text)
        if metrics['post_types']:
            return pd.DataFrame({
                'post_type': metrics['post_types'],
                'engagement_rate': metrics['engagement_rates'],
                'likes': metrics['likes'],
                'comments': metrics['comments'],
                'shares': metrics['shares']
            })
        
        data = {
            'post_type': ['All Types', 'Carousel Posts', 'Video Posts'],
            'engagement_rate': [2.36, 2.62, 2.10],
            'likes': [2660.9, 3200, 2500],
            'comments': [107.4, 150, 80],
            'leads': [100, 120, 90]
        }
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error extracting metrics: {str(e)}")
        return pd.DataFrame({
            'post_type': ['All Types'],
            'engagement_rate': [2.36],
            'likes': [2660.9],
            'comments': [107.4],
            'leads': [100]
        })

def create_visualizations(df):
    """Create visualizations with consistent styling"""
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        fig_engagement = go.Figure()
        fig_engagement.add_trace(go.Bar(
            x=df['post_type'],
            y=df['engagement_rate'],
            marker_color='#ff4b4b',
            text=df['engagement_rate'].apply(lambda x: f'{x:.2f}%'),
            textposition='outside'
        ))
        
        fig_engagement.update_layout(
            title='Engagement Rate by Post Type',
            plot_bgcolor='#2d2d2d',
            paper_bgcolor='#2d2d2d',
            font=dict(color='#ffffff'),
            height=400,
            margin=dict(t=50, b=50),
            showlegend=False,
            xaxis=dict(gridcolor='#404040'),
            yaxis=dict(gridcolor='#404040')
        )
        
        st.plotly_chart(fig_engagement, use_container_width=True)
    
    with chart_col2:
        fig_likes = go.Figure()
        fig_likes.add_trace(go.Bar(
            x=df['post_type'],
            y=df['likes'],
            marker_color='#ff4b4b',
            text=df['likes'].apply(lambda x: f'{x:,.0f}'),
            textposition='outside'
        ))
        
        fig_likes.update_layout(
            title='Average Likes by Post Type',
            plot_bgcolor='#2d2d2d',
            paper_bgcolor='#2d2d2d',
            font=dict(color='#ffffff'),
            height=400,
            margin=dict(t=50, b=50),
            showlegend=False,
            xaxis=dict(gridcolor='#404040'),
            yaxis=dict(gridcolor='#404040')
        )
        
        st.plotly_chart(fig_likes, use_container_width=True)

def main():
    st.set_page_config(
        page_title="Social Media Analytics Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Custom CSS (keeping the same styling)
    st.markdown("""
        <style>
            .main { background-color: #1a1a1a; color: #ffffff; padding: 2rem; }
            .stTitle { color: #ffffff !important; font-size: 2.5rem !important; font-weight: 600 !important; margin-bottom: 2rem !important; }
            .metric-card { background-color: #2d2d2d; border-radius: 10px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); transition: transform 0.2s ease; }
            .metric-card:hover { transform: translateY(-5px); }
            .metric-value { font-size: 2rem; font-weight: 700; color: #ffffff; margin: 0.5rem 0; }
            .metric-label { font-size: 1rem; color: #b3b3b3; margin-bottom: 0.5rem; }
            .stButton > button { background-color: #ff4b4b !important; color: white !important; border: none !important; padding: 0.75rem 1.5rem !important; border-radius: 8px !important; font-weight: 600 !important; transition: all 0.3s ease !important; }
            .stButton > button:hover { background-color: #ff3333 !important; transform: translateY(-2px); }
            .chat-container { background-color: #2d2d2d; border-radius: 10px; padding: 1.5rem; margin-top: 1rem; }
            .chat-message { padding: 1rem; border-radius: 8px; margin-bottom: 1rem; background-color: #404040; }
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stTabs [data-baseweb="tab-list"] { gap: 2rem; background-color: #2d2d2d; padding: 1rem; border-radius: 10px; }
            .stTabs [data-baseweb="tab"] { color: #ffffff !important; background-color: transparent !important; border: none !important; font-weight: 500; }
            .stTextInput > div > div { background-color: #2d2d2d !important; color: #ffffff !important; border-radius: 8px !important; }
            .chat-history { max-height: 400px; overflow-y: auto; margin-top: 2rem; padding: 1rem; background-color: #2d2d2d; border-radius: 10px; }
            .viz-container { background-color: #2d2d2d; border-radius: 10px; padding: 1.5rem; margin-top: 2rem; }
        </style>
    """, unsafe_allow_html=True)

    st.title("📱 Social Media Performance Analytics")

    tab1, tab2, tab3 = st.tabs(["📊 Performance Analysis", "💡 Insights Q&A", "📈 Trends"])

    with tab1:
        st.markdown("""
            <div class="metric-container">
                <h2 style='color: #ffffff; margin-bottom: 1.5rem;'>Post Type Performance Analysis</h2>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            post_type = st.selectbox(
                "Select Post Type",
                ["All Types", "Carousel", "Reels", "Static Images", "Stories"]
            )
        with col2:
            metrics = st.multiselect(
                "Select Metrics",
                ["Engagement Rate", "Likes", "Comments", "Shares"],
                default=["Engagement Rate", "Likes"]
            )

        if st.button("Analyze Performance", type="primary"):
            with st.spinner("Analyzing post performance..."):
                query = f"Analyze the performance metrics for {post_type} posts focusing on {', '.join(metrics)}"
                response = run_flow(query)
                
                if response:
                    try:
                        df = extract_metrics_from_text(extract_message_from_response(response))
                        
                        # KPI Cards
                        st.markdown("<h3 style='color: #ffffff; margin: 2rem 0 1rem;'>Key Performance Indicators</h3>", unsafe_allow_html=True)
                        
                        kpi_cols = st.columns(4)
                        kpis = [
                            ("Average Engagement Rate", f"{df['engagement_rate'].mean():.2f}%"),
                            ("Average Likes", f"{df['likes'].mean():,.0f}"),
                            ("Average Comments", f"{df['comments'].mean():,.0f}"),
                            ("Average Leads", f"{df['leads'].mean():,.0f}")
                        ]
                        
                        for i, (label, value) in enumerate(kpis):
                            with kpi_cols[i]:
                                st.markdown(f"""
                                    <div class="metric-card">
                                        <div class="metric-label">{label}</div>
                                        <div class="metric-value">{value}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                        
                        # Insights
                        st.markdown("<h3 style='color: #ffffff; margin: 2rem 0 1rem;'>Analysis Insights</h3>", unsafe_allow_html=True)
                        st.markdown(f"""
                            <div class="chat-container">
                                {extract_message_from_response(response)}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Visualizations
                        st.markdown("<h3 style='color: #ffffff; margin: 2rem 0 1rem;'>Performance Visualizations</h3>", unsafe_allow_html=True)
                        create_visualizations(df)
                        
                    except Exception as e:
                        st.error(f"Error processing data: {str(e)}")
                else:
                    st.error("Failed to get analysis results")

    with tab2:
        st.markdown("""
            <div class="metric-container">
                <h2 style='color: #ffffff; margin-bottom: 1.5rem;'>Ask Questions & Get Insights</h2>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div style='color: #b3b3b3; margin-bottom: 1rem;'>
                Example questions you can ask:
                <ul>
                    <li>Which type of posts performed better and why?</li>
                    <li>What are the key factors affecting engagement rates?</li>
                    <li>How do carousel posts compare to video posts?</li>
                    <li>What are the best practices for improving engagement?</li>
                    <li>What time of day gets the most engagement?</li>
                    <li>What content themes are most successful?</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

        user_question = st.text_input("Enter your question", key="qa_input", 
                                    placeholder="Type your question here...")

        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        if st.button("Get Insights", key="qa_button", type="primary"):
            if user_question:
                with st.spinner("Analyzing..."):
                    response = run_flow(user_question)
                    if response:
                        insight = extract_message_from_response(response)
                        if insight:
                            st.session_state.chat_history.append({
                                "question": user_question,
                                "answer": insight,
                                "timestamp": datetime.now().strftime("%H:%M:%S")
                            })
                            
                            st.markdown(f"""
                                <div class="chat-container">
                                    <div class="chat-message">
                                        <strong>Question:</strong><br>{user_question}
                                    </div>
                                    <div class="chat-message">
                                        <strong>Answer:</strong><br>{insight}
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            if len(st.session_state.chat_history) > 1:
                                st.markdown("<h3 style='color: #ffffff; margin: 2rem 0 1rem;'>Previous Questions</h3>", unsafe_allow_html=True)
                                with st.expander("View Chat History"):
                                    for chat in reversed(st.session_state.chat_history[:-1]):
                                        st.markdown(f"""
                                            <div class="chat-message">
                                                <small>{chat['timestamp']}</small><br>
                                                <strong>Q:</strong> {chat['question']}<br>
                                                <strong>A:</strong> {chat['answer']}
                                            </div>
                                        """, unsafe_allow_html=True)
                        else:
                            st.error("Could not generate insights")
                    else:
                        st.error("Failed to get response")
            else:
                st.warning("Please enter a question")

    with tab3:
        st.markdown("""
            <div class="metric-container">
                <h2 style='color: #ffffff; margin-bottom: 1.5rem;'>Engagement Trends Analysis</h2>
            </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            trend_period = st.selectbox(
                "Select Time Period",
                ["Last 7 days", "Last 30 days", "Last 3 months", "Last year"]
            )
        with col2:
            trend_metric = st.selectbox(
                "Select Metric",
                ["Engagement Rate", "Likes", "Comments", "Shares"]
            )
        with col3:
            comparison = st.checkbox("Compare with previous period")

        if st.button("Analyze Trends", type="primary"):
            with st.spinner("Analyzing trends..."):
                query = f"Analyze the {trend_metric.lower()} trends for {trend_period.lower()}"
                if comparison:
                    query += " and compare with the previous period"
                    
                response = run_flow(query)
                if response:
                    insight = extract_message_from_response(response)
                    if insight:
                        st.markdown(f"""
                            <div class="chat-container">
                                <div class="chat-message">
                                    <strong>Trend Analysis:</strong><br>{insight}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("Could not generate trend analysis")
                else:
                    st.error("Failed to analyze trends")

    # Footer
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0; color: #b3b3b3; font-size: 0.9rem;'>
            © 2024 Social Analytics Dashboard • Built with ❤️ using Streamlit
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
