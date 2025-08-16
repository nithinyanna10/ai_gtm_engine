"""
Streamlit dashboard for monitoring the AI GTM Engine.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any

# Configure Streamlit page
st.set_page_config(
    page_title="AI GTM Engine Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_BASE_URL = "http://localhost:8000"

def make_api_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Make API request to the backend."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

def main():
    """Main dashboard function."""
    
    # Header
    st.title("🚀 AI GTM Engine Dashboard")
    st.markdown("Advanced AI-powered Go-To-Market engine for intelligent lead generation and outreach")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Overview", "Leads", "Signals", "Outreach", "Analytics", "Signal Details", "Settings"]
    )
    
    if page == "Overview":
        show_overview()
    elif page == "Leads":
        show_leads()
    elif page == "Signals":
        show_signals()
    elif page == "Outreach":
        show_outreach()
    elif page == "Analytics":
        show_analytics()
    elif page == "Signal Details":
        show_signal_details()
    elif page == "Settings":
        show_settings()

def show_overview():
    """Show dashboard overview."""
    st.header("📊 Dashboard Overview")
    
    # Get analytics data
    analytics = make_api_request("/analytics/overview")
    
    if "error" in analytics:
        st.error(f"Failed to load analytics: {analytics['error']}")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Leads",
            value=analytics.get("total_leads", 0),
            delta=None
        )
    
    with col2:
        st.metric(
            label="High Intent Leads",
            value=analytics.get("high_intent_leads", 0),
            delta=None
        )
    
    with col3:
        st.metric(
            label="Total Signals",
            value=analytics.get("total_signals", 0),
            delta=analytics.get("recent_signals_7d", 0)
        )
    
    with col4:
        st.metric(
            label="Total Outreach",
            value=analytics.get("total_outreach", 0),
            delta=analytics.get("recent_outreach_7d", 0)
        )
    
    # Recent activity
    st.subheader("🔄 Recent Activity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"📈 {analytics.get('recent_signals_7d', 0)} new signals in the last 7 days")
    
    with col2:
        st.info(f"📧 {analytics.get('recent_outreach_7d', 0)} new outreach attempts in the last 7 days")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    with col2:
        if st.button("📊 View Analytics"):
            st.switch_page("Analytics")
    
    with col3:
        if st.button("👥 Manage Leads"):
            st.switch_page("Leads")

def show_leads():
    """Show leads management page."""
    st.header("👥 Lead Management")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_score = st.slider("Minimum Intent Score", 0.0, 1.0, 0.5, 0.1)
    
    with col2:
        limit = st.number_input("Number of Leads", min_value=10, max_value=1000, value=100)
    
    with col3:
        if st.button("🔄 Refresh Leads"):
            st.rerun()
    
    # Get leads
    leads_data = make_api_request(f"/leads?limit={limit}&min_score={min_score}")
    
    if "error" in leads_data:
        st.error(f"Failed to load leads: {leads_data['error']}")
        return
    
    if not leads_data:
        st.warning("No leads found matching the criteria.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(leads_data)
    
    # Display leads table
    st.subheader(f"📋 Leads (Showing {len(df)} results)")
    
    # Format the DataFrame for display
    display_df = df.copy()
    display_df['intent_score'] = display_df['intent_score'].apply(lambda x: f"{x:.2f}")
    
    # Add last_updated if it doesn't exist
    if 'last_updated' not in display_df.columns:
        display_df['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # Add tech stack info
    if 'tech_stack' in display_df.columns:
        display_df['tech_stack_display'] = display_df['tech_stack'].apply(lambda x: ', '.join(x[:3]) if isinstance(x, list) else str(x)[:30])
    else:
        display_df['tech_stack_display'] = 'N/A'
    
    # Select columns to display
    columns_to_show = ['company_name', 'domain', 'industry', 'employee_count', 'revenue_range', 'intent_score', 'tech_stack_display']
    st.dataframe(display_df[columns_to_show], use_container_width=True)
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Companies", len(df))
    with col2:
        high_intent = len(df[df['intent_score'].astype(float) > 0.8])
        st.metric("High Intent (>0.8)", high_intent)
    with col3:
        avg_score = df['intent_score'].astype(float).mean()
        st.metric("Avg Intent Score", f"{avg_score:.2f}")
    with col4:
        top_industry = df['industry'].mode().iloc[0] if len(df) > 0 else "N/A"
        st.metric("Top Industry", top_industry)
    
    # Lead details
    st.subheader("🔍 Lead Details")
    
    if st.selectbox("Select a lead to view details:", df['company_name'].tolist()):
        selected_lead = df[df['company_name'] == st.session_state.get('selected_lead', df['company_name'].iloc[0])].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Company:** {selected_lead['company_name']}")
            st.write(f"**Domain:** {selected_lead['domain']}")
            st.write(f"**Industry:** {selected_lead['industry']}")
            st.write(f"**Employees:** {selected_lead['employee_count']}")
        
        with col2:
            st.write(f"**Intent Score:** {selected_lead['intent_score']:.2f}")
            st.write(f"**Revenue Range:** {selected_lead.get('revenue_range', 'N/A')}")
            st.write(f"**Location:** {selected_lead.get('location', 'N/A')}")
            st.write(f"**Primary Tech:** {selected_lead.get('primary_tech', 'N/A')}")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 Collect Real Signals", key="collect_signals"):
                # Get real signals for this lead
                signals = make_api_request(f"/leads/{selected_lead['id']}/signals")
                if "error" not in signals and signals:
                    st.success(f"Found {len(signals)} real signals!")
                    st.json(signals[:3])  # Show first 3 signals
                else:
                    st.info("No signals found yet. Try again in a moment.")
        
        with col2:
            if st.button("📧 Generate Content", key="generate_content"):
                st.session_state['selected_lead_id'] = selected_lead['id']
                st.info("Content generation feature coming soon!")
        
        with col3:
            if st.button("📊 View Signals", key="view_signals"):
                st.session_state['selected_lead_id'] = selected_lead['id']
                st.info("Signal details feature coming soon!")
        
        # Data Sources Section
        st.subheader("🔍 Data Sources & Signals")
        
        # Get real signals for this company
        signals = make_api_request(f"/leads/{selected_lead['id']}/signals")
        
        if "error" not in signals and signals:
            # Group signals by source
            sources = {}
            for signal in signals:
                source = signal.get('source', 'unknown')
                if source not in sources:
                    sources[source] = []
                sources[source].append(signal)
            
            # Display sources with counts
            col1, col2, col3 = st.columns(3)
            with col1:
                if 'github' in sources:
                    st.metric("GitHub Signals", len(sources['github']))
                    st.info("🔧 Found repositories with authentication/security issues")
            with col2:
                if 'news' in sources:
                    st.metric("News Signals", len(sources['news']))
                    st.info("📰 Found security-related news articles")
            with col3:
                if 'reddit' in sources:
                    st.metric("Reddit Signals", len(sources['reddit']))
                    st.info("💬 Found community discussions")
            
            # Show sample signals
            st.subheader("📊 Sample Signals")
            for source, source_signals in sources.items():
                with st.expander(f"{source.upper()} Signals ({len(source_signals)})"):
                    for i, signal in enumerate(source_signals[:3]):  # Show first 3
                        st.write(f"**{i+1}. {signal.get('signal_type', 'Unknown')}**")
                        st.write(f"Content: {signal.get('content', 'No content')[:100]}...")
                        st.write(f"Confidence: {signal.get('confidence', 0):.2f}")
                        st.write("---")
        else:
            st.info("No signals found yet. Click 'Collect Real Signals' to gather data.")
        
        # AI Summarization Section
        st.subheader("🤖 AI Analysis & Summary")
        
        if "error" not in signals and signals:
            # Prepare data for ChatGPT
            company_name = selected_lead['company_name']
            industry = selected_lead.get('industry', 'Unknown')
            employee_count = selected_lead.get('employee_count', 'Unknown')
            tech_stack = selected_lead.get('tech_stack', [])
            
            # Create summary prompt
            summary_prompt = f"""
            Company: {company_name}
            Industry: {industry}
            Employees: {employee_count}
            Tech Stack: {', '.join(tech_stack) if isinstance(tech_stack, list) else tech_stack}
            
            Found {len(signals)} signals from various sources. Please provide:
            1. Key security/authentication challenges identified
            2. Business impact assessment
            3. Recommended outreach approach
            4. Priority level (High/Medium/Low)
            """
            
            # Add signal details to prompt
            for i, signal in enumerate(signals[:5]):  # Include first 5 signals
                summary_prompt += f"\nSignal {i+1}: {signal.get('signal_type', 'Unknown')} - {signal.get('content', 'No content')[:100]}"
            
            # Display AI summary (simulated for now)
            with st.expander("🤖 AI Analysis Summary"):
                st.write("**Key Findings:**")
                st.write("• Authentication vulnerabilities detected in GitHub repositories")
                st.write("• Security-related news mentions indicate awareness of issues")
                st.write("• High intent score suggests urgent need for solutions")
                
                st.write("**Business Impact:**")
                st.write("• Potential security risks affecting user trust")
                st.write("• Compliance concerns in financial/tech sectors")
                st.write("• Opportunity for immediate engagement")
                
                st.write("**Recommended Approach:**")
                st.write("• Personalized outreach highlighting specific vulnerabilities")
                st.write("• Case studies from similar companies")
                st.write("• Free security assessment offer")
                
                st.write("**Priority Level:** 🔴 HIGH")
                
                # Add a button to regenerate with real ChatGPT
                if st.button("🔄 Regenerate with ChatGPT"):
                    st.info("Connecting to ChatGPT API... (Feature coming soon)")
        else:
            st.info("Collect signals first to generate AI analysis.")

def show_signals():
    """Show signals page."""
    st.header("📡 Signal Monitoring")
    
    # Get all signals from all leads
    all_signals = make_api_request("/signals")
    
    if "error" not in all_signals and all_signals and len(all_signals) > 0:
        # Convert to DataFrame
        df = pd.DataFrame(all_signals)
        
        # Real-time signal statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Signals", len(df))
        with col2:
            unique_sources = df['source'].nunique() if 'source' in df.columns else 0
            st.metric("Data Sources", unique_sources)
        with col3:
            avg_confidence = df['confidence'].mean() if 'confidence' in df.columns else 0
            st.metric("Avg Confidence", f"{avg_confidence:.2f}")
        with col4:
            high_confidence = len(df[df['confidence'] > 0.7]) if 'confidence' in df.columns else 0
            st.metric("High Confidence", high_confidence)
        
        # Signals by Type (Real Data)
        if 'signal_type' in df.columns:
            signal_counts = df['signal_type'].value_counts()
            fig = px.pie(
                values=signal_counts.values,
                names=signal_counts.index,
                title='📊 Signals by Type (Real Data)',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        # Signals by Source
        if 'source' in df.columns:
            source_counts = df['source'].value_counts()
            fig = px.bar(
                x=source_counts.index,
                y=source_counts.values,
                title='📡 Signals by Data Source',
                labels={'x': 'Source', 'y': 'Count'},
                color=source_counts.values,
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent Signals Timeline
        if 'signal_date' in df.columns:
            df['signal_date'] = pd.to_datetime(df['signal_date'])
            recent_signals = df.sort_values('signal_date', ascending=False).head(10)
            
            fig = px.timeline(
                recent_signals,
                x_start='signal_date',
                y='signal_type',
                color='confidence',
                title='⏰ Recent Signals Timeline',
                hover_data=['content']
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No signals data available. Collect signals from leads first.")
    
    # Lead-specific signals
    st.subheader("🔍 Lead Signals")
    
    lead_id = st.session_state.get('selected_lead_id')
    if lead_id:
        signals = make_api_request(f"/leads/{lead_id}/signals")
        
        if "error" not in signals and signals:
            df = pd.DataFrame(signals)
            
            # Format dates
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['signal_date'] = pd.to_datetime(df['signal_date'])
            
            # Display signals
            st.dataframe(
                df[['signal_type', 'source', 'content', 'confidence', 'created_at']],
                use_container_width=True
            )
            
            # Signal timeline
            fig = px.timeline(
                df,
                x_start='signal_date',
                y='signal_type',
                color='confidence',
                title='Signal Timeline'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No signals found for this lead.")
    else:
        st.info("Select a lead from the Leads page to view their signals.")

def show_outreach():
    """Show outreach management page."""
    st.header("📧 Outreach Management")
    
    # Get all leads for prioritization
    leads = make_api_request("/leads")
    
    if "error" not in leads and leads:
        # Prioritize leads by intent score
        high_priority = [lead for lead in leads if lead.get('intent_score', 0) > 0.8]
        medium_priority = [lead for lead in leads if 0.6 <= lead.get('intent_score', 0) <= 0.8]
        low_priority = [lead for lead in leads if lead.get('intent_score', 0) < 0.6]
        
        # Priority Summary
        st.subheader("🎯 Lead Priority Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔴 High Priority", len(high_priority))
            if high_priority:
                st.write("**Companies:**")
                for lead in high_priority[:3]:
                    st.write(f"• {lead['company_name']} ({lead['intent_score']:.2f})")
        with col2:
            st.metric("🟡 Medium Priority", len(medium_priority))
            if medium_priority:
                st.write("**Companies:**")
                for lead in medium_priority[:3]:
                    st.write(f"• {lead['company_name']} ({lead['intent_score']:.2f})")
        with col3:
            st.metric("🟢 Low Priority", len(low_priority))
            if low_priority:
                st.write("**Companies:**")
                for lead in low_priority[:3]:
                    st.write(f"• {lead['company_name']} ({lead['intent_score']:.2f})")
        
        # High Priority Companies Analysis
        if high_priority:
            st.subheader("🚨 High Priority Companies Analysis")
            
            for lead in high_priority:
                with st.expander(f"🔴 {lead['company_name']} (Score: {lead['intent_score']:.2f})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Industry:** {lead.get('industry', 'N/A')}")
                        st.write(f"**Employees:** {lead.get('employee_count', 'N/A')}")
                        st.write(f"**Revenue:** {lead.get('revenue_range', 'N/A')}")
                    with col2:
                        st.write(f"**Tech Stack:** {', '.join(lead.get('tech_stack', []))}")
                        st.write(f"**Location:** {lead.get('location', 'N/A')}")
                        st.write(f"**Primary Tech:** {lead.get('primary_tech', 'N/A')}")
                    
                    # Get signals for this company
                    signals = make_api_request(f"/leads/{lead['id']}/signals")
                    if "error" not in signals and signals:
                        st.write(f"**Signals Found:** {len(signals)}")
                        st.write("**Key Issues:**")
                        for signal in signals[:3]:
                            st.write(f"• {signal.get('signal_type', 'Unknown')}: {signal.get('content', '')[:80]}...")
                    
                    # AI-generated outreach strategy
                    st.write("**🤖 AI Outreach Strategy:**")
                    st.write("• **Approach:** Personalized security assessment offer")
                    st.write("• **Timing:** Immediate (high urgency detected)")
                    st.write("• **Channel:** LinkedIn + Email combination")
                    st.write("• **Value Prop:** Free security audit + case studies")
    
    # Content generation
    st.subheader("🤖 AI Content Generation")
    
    lead_id = st.session_state.get('selected_lead_id')
    if lead_id:
        # Contact information form
        with st.form("contact_info"):
            st.write("**Contact Information**")
            contact_name = st.text_input("Contact Name")
            contact_title = st.text_input("Contact Title")
            contact_email = st.text_input("Contact Email")
            
            if st.form_submit_button("Generate Content"):
                contact_info = {
                    "name": contact_name,
                    "title": contact_title,
                    "email": contact_email
                }
                
                content = make_api_request(
                    f"/leads/{lead_id}/generate-content",
                    method="POST",
                    data=contact_info
                )
                
                if "error" not in content:
                    st.session_state['generated_content'] = content['content']
                    st.success("Content generated successfully!")
                else:
                    st.error(f"Failed to generate content: {content['error']}")
        
        # Display generated content
        if 'generated_content' in st.session_state:
            st.subheader("📝 Generated Content")
            
            content = st.session_state['generated_content']
            
            tabs = st.tabs(["Email", "LinkedIn", "Video Script", "Call Script"])
            
            with tabs[0]:
                st.text_area("Email Content", content.get('email', ''), height=200)
                if st.button("📧 Send Email", key="send_email"):
                    st.info("Email sending functionality would be implemented here.")
            
            with tabs[1]:
                st.text_area("LinkedIn Message", content.get('linkedin', ''), height=200)
                if st.button("💼 Send LinkedIn", key="send_linkedin"):
                    st.info("LinkedIn sending functionality would be implemented here.")
            
            with tabs[2]:
                st.text_area("Video Script", content.get('video_script', ''), height=200)
                if st.button("🎥 Generate Video", key="generate_video"):
                    st.info("Video generation functionality would be implemented here.")
            
            with tabs[3]:
                st.text_area("Call Script", content.get('call_script', ''), height=200)
                if st.button("📞 Schedule Call", key="schedule_call"):
                    st.info("Call scheduling functionality would be implemented here.")
    else:
        st.info("Select a lead from the Leads page to generate outreach content.")
    
    # Outreach history
    st.subheader("📋 Outreach History")
    
    if lead_id:
        outreach_history = make_api_request(f"/leads/{lead_id}/outreach")
        
        if "error" not in outreach_history and outreach_history:
            df = pd.DataFrame(outreach_history)
            
            # Format dates
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            # Display outreach history
            st.dataframe(
                df[['channel', 'status', 'recipient_name', 'created_at']],
                use_container_width=True
            )
        else:
            st.info("No outreach history found for this lead.")

def show_analytics():
    """Show analytics page."""
    st.header("📊 Analytics Dashboard")
    
    # Get analytics data
    analytics = make_api_request("/analytics/overview")
    leads = make_api_request("/leads")
    all_signals = make_api_request("/signals")
    
    if "error" not in analytics and analytics:
        # Key metrics with beautiful styling
        st.markdown("### 🎯 Key Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Total Leads", 
                analytics.get('total_leads', 0),
                delta=f"+{analytics.get('recent_leads_7d', 0)} this week"
            )
        with col2:
            st.metric(
                "Total Signals", 
                analytics.get('total_signals', 0),
                delta=f"+{analytics.get('recent_signals_7d', 0)} this week"
            )
        with col3:
            st.metric(
                "High Intent Leads", 
                analytics.get('high_intent_leads', 0),
                delta="High priority"
            )
        with col4:
            st.metric(
                "Conversion Rate", 
                f"{(analytics.get('high_intent_leads', 0) / max(analytics.get('total_leads', 1), 1) * 100):.1f}%",
                delta="Target: 60%"
            )
        
        # Company Distribution by Industry
        if "error" not in leads and leads:
            st.markdown("### 🏢 Company Distribution")
            df_leads = pd.DataFrame(leads)
            
            col1, col2 = st.columns(2)
            with col1:
                if 'industry' in df_leads.columns:
                    industry_counts = df_leads['industry'].value_counts()
                    fig = px.pie(
                        values=industry_counts.values,
                        names=industry_counts.index,
                        title='📊 Companies by Industry',
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'intent_score' in df_leads.columns:
                    fig = px.histogram(
                        df_leads,
                        x='intent_score',
                        nbins=10,
                        title='📈 Intent Score Distribution',
                        labels={'intent_score': 'Intent Score', 'count': 'Number of Companies'},
                        color_discrete_sequence=['#636EFA']
                    )
                    fig.add_vline(x=0.8, line_dash="dash", line_color="red", annotation_text="High Priority Threshold")
                    st.plotly_chart(fig, use_container_width=True)
        
        # Signal Analysis
        if "error" not in all_signals and all_signals:
            st.markdown("### 📡 Signal Analysis")
            df_signals = pd.DataFrame(all_signals)
            
            col1, col2 = st.columns(2)
            with col1:
                if 'source' in df_signals.columns:
                    source_counts = df_signals['source'].value_counts()
                    fig = px.bar(
                        x=source_counts.index,
                        y=source_counts.values,
                        title='📊 Signals by Source',
                        labels={'x': 'Data Source', 'y': 'Signal Count'},
                        color=source_counts.values,
                        color_continuous_scale='plasma'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'confidence' in df_signals.columns:
                    fig = px.box(
                        df_signals,
                        y='confidence',
                        title='📊 Signal Confidence Distribution',
                        labels={'confidence': 'Confidence Score'},
                        color_discrete_sequence=['#00CC96']
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # Performance Trends
        st.markdown("### 📈 Performance Trends")
        col1, col2 = st.columns(2)
        with col1:
            # Simulated trend data
            dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
            trend_data = pd.DataFrame({
                'date': dates,
                'signals': np.random.randint(5, 20, 30),
                'leads': np.random.randint(1, 5, 30)
            })
            
            fig = px.line(
                trend_data,
                x='date',
                y=['signals', 'leads'],
                title='📈 Daily Activity Trends',
                labels={'value': 'Count', 'variable': 'Metric'},
                color_discrete_sequence=['#636EFA', '#00CC96']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top performing companies
            if "error" not in leads and leads:
                df_leads = pd.DataFrame(leads)
                top_companies = df_leads.nlargest(5, 'intent_score')
                
                fig = px.bar(
                    top_companies,
                    x='company_name',
                    y='intent_score',
                    title='🏆 Top Performing Companies',
                    labels={'company_name': 'Company', 'intent_score': 'Intent Score'},
                    color='intent_score',
                    color_continuous_scale='viridis'
                )
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)

def show_signal_details():
    """Show detailed signal information."""
    st.header("🔍 Signal Details")
    st.markdown("Detailed view of all signals with company information and sources")
    
    # Get all signals
    signals = make_api_request("/signals")
    
    if "error" in signals:
        st.error(f"Failed to load signals: {signals['error']}")
        return
    
    if not signals:
        st.info("No signals found.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(signals)
    
    # Format dates
    df['signal_date'] = pd.to_datetime(df['signal_date'])
    
    # Display signals table
    st.subheader("📊 All Signals")
    
    # Add filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        signal_types = df['signal_type'].unique()
        selected_type = st.selectbox("Filter by Signal Type", ["All"] + list(signal_types))
    
    with col2:
        companies = df['company_name'].unique()
        selected_company = st.selectbox("Filter by Company", ["All"] + list(companies))
    
    with col3:
        sources = df['source'].unique()
        selected_source = st.selectbox("Filter by Source", ["All"] + list(sources))
    
    # Apply filters
    filtered_df = df.copy()
    if selected_type != "All":
        filtered_df = filtered_df[filtered_df['signal_type'] == selected_type]
    if selected_company != "All":
        filtered_df = filtered_df[filtered_df['company_name'] == selected_company]
    if selected_source != "All":
        filtered_df = filtered_df[filtered_df['source'] == selected_source]
    
    # Display filtered data
    st.dataframe(
        filtered_df[['company_name', 'signal_type', 'source', 'content', 'confidence', 'signal_date']],
        use_container_width=True
    )
    
    # Signal breakdown
    st.subheader("📈 Signal Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Signals by company
        company_signals = filtered_df.groupby('company_name').size().reset_index(name='count')
        fig = px.bar(
            company_signals,
            x='company_name',
            y='count',
            title='Signals by Company'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Signals by type
        type_signals = filtered_df.groupby('signal_type').size().reset_index(name='count')
        fig = px.pie(
            type_signals,
            values='count',
            names='signal_type',
            title='Signals by Type'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed signal view
    st.subheader("🔍 Signal Details")
    
    if not filtered_df.empty:
        selected_signal = st.selectbox(
            "Select a signal to view details:",
            filtered_df.index,
            format_func=lambda x: f"{filtered_df.iloc[x]['company_name']} - {filtered_df.iloc[x]['signal_type']} ({filtered_df.iloc[x]['signal_date'].strftime('%Y-%m-%d %H:%M')})"
        )
        
        if selected_signal is not None:
            signal = filtered_df.iloc[selected_signal]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Company:**", signal['company_name'])
                st.write("**Signal Type:**", signal['signal_type'])
                st.write("**Source:**", signal['source'])
                st.write("**Confidence:**", f"{signal['confidence']:.2f}")
                st.write("**Date:**", signal['signal_date'].strftime('%Y-%m-%d %H:%M'))
            
            with col2:
                st.write("**Content:**")
                st.text_area("Signal Content", signal['content'], height=100, disabled=True, label_visibility="collapsed")
                
                if 'keywords_found' in signal and signal['keywords_found']:
                    st.write("**Keywords Found:**")
                    st.write(", ".join(signal['keywords_found']))

def show_settings():
    """Show settings page."""
    st.header("⚙️ Settings")
    
    st.subheader("🔧 Configuration")
    
    # API Status
    st.write("**API Status**")
    health = make_api_request("/health")
    
    if "error" not in health:
        st.success("✅ API is running")
    else:
        st.error("❌ API is not responding")
    
    # Configuration options
    st.subheader("📋 System Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Scoring Weights**")
        st.write("- GitHub Activity: 25%")
        st.write("- Community Signals: 20%")
        st.write("- Job Postings: 20%")
        st.write("- News/Product: 15%")
        st.write("- Technographic: 10%")
        st.write("- Firmographic: 10%")
    
    with col2:
        st.write("**Thresholds**")
        st.write("- High Intent: 0.7")
        st.write("- Medium Intent: 0.5")
        st.write("- Recent Activity Window: 30 days")
        st.write("- Trigger Freshness: 7 days")
    
    # Data sources
    st.subheader("🔗 Data Sources")
    
    sources = [
        "GitHub API",
        "Reddit API", 
        "LinkedIn Jobs API",
        "Google News API",
        "Clearbit API",
        "BuiltWith API"
    ]
    
    for source in sources:
        st.write(f"• {source}")

if __name__ == "__main__":
    main()
