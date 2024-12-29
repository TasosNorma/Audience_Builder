import streamlit as st
import json
from pathlib import Path
import pandas as pd

def view_traces():
    st.title("Content Processor Traces")

    traces_dir = Path("traces")
    trace_files = list(traces_dir.glob("trace_*.json"))

    traces_data = []
    for trace_file in trace_files:
        with open(trace_file) as f:
            trace = json.load(f)
            total_duration = sum(step["duration"] for step in trace["steps"])
            traces_data.append({
                "Timestamp": trace["start_time"],
                "URL": trace["url"],
                "Status": trace["status"],
                "Total Duration": f"{total_duration:.2f}s",
                "File": trace_file.name
            })
    
    df = pd.DataFrame(traces_data)
    st.dataframe(df)

    # View detailed trace
    selected_trace = st.selectbox("Select trace to view details", trace_files)
    if selected_trace:
        with open(selected_trace) as f:
            trace = json.load(f)

        st.header("Trace Details")

        # Show steps timing
        st.subheader("Steps")
        steps_df = pd.DataFrame(trace["steps"])
        st.dataframe(steps_df)
        
        # Add tabs for different content views
        tab1, tab2, tab3 = st.tabs(["Process Steps", "Final LLM Prompt", "Results"])
        
        with tab1:
            st.subheader("Article Preview")
            st.text_area("Primary Article", trace["content"]["article_preview"], height=200)
            
            st.subheader("Secondary Articles")
            st.text_area("Secondary Content", trace["content"].get("secondary_articles", "Not found"), height=200)
        
        with tab2:
            st.subheader("Prompt Template")
            st.text_area("Template", trace["content"].get("prompt_template", "Not found"), height=200)
            
            st.subheader("Final Formatted Prompt")
            st.text_area("Exact Prompt Sent to LLM", trace["content"].get("final_prompt", "Not found"), height=400)
        
        with tab3:
            st.subheader("Generated Tweets")
            for i, tweet in enumerate(trace["content"]["tweets"], 1):
                st.text_area(f"Tweet {i}", tweet, height=100)



if __name__ == "__main__":
    view_traces()