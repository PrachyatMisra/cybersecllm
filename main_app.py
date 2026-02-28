# main_app.py - Complete Streamlit Dashboard
"""
Cybersecurity Knowledge Graph - Main Application
Complete LLM-Powered IDS Knowledge Graph System
"""

import streamlit as st
import streamlit.components.v1 as components
import asyncio
import json
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go

from neo4j_handler_complete import Neo4jHandler
from mitre_attack_ingest_complete import MitreAttackIngester
from graph_builder import GraphBuilder
from llm_entity_extractor import LLMEntityExtractor
from youtube_ingest import YouTubeIngester
from pdf_ingest import PDFIngester

# Page Configuration
st.set_page_config(
    page_title="CyberGraph Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject Custom UI & CSS
try:
    with open("particles.html", "r", encoding="utf-8") as f:
        particles_html = f.read()
        
    st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 0rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }
        iframe[title="streamlit.components.v1.html"] {
            height: 90vh !important;
            border-radius: 12px;
        }
    </style>
    """, unsafe_allow_html=True)
    st.components.v1.html(particles_html, height=1, width=1)
except FileNotFoundError:
    pass

# Initialize Session State
if 'neo4j_handler' not in st.session_state:
    st.session_state.neo4j_handler = None
if 'graph_stats' not in st.session_state:
    st.session_state.graph_stats = {}

def init_connections():
    """Initialize database connections"""
    try:
        handler = Neo4jHandler(
            uri=st.secrets.get("neo4j_uri", "bolt://localhost:7687"),
            user=st.secrets.get("neo4j_user", "neo4j"),
            password=st.secrets.get("neo4j_password", "password")
        )
        st.session_state.neo4j_handler = handler
        return True
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return False

def main():
    st.title("🛡️ Cybersecurity Knowledge Graph Intelligence System")
    st.markdown("**LLM-Powered IDS & Threat Intelligence Platform**")
    
    # Sidebar Navigation
    with st.sidebar:
        st.header("🎛️ Control Panel")
        
        if st.button("🔌 Connect to Neo4j"):
            if init_connections():
                st.success("✅ Connected to Neo4j")
        
        page = st.radio(
            "Navigation",
            ["🌐 3D Live Dashboard", "📥 Data Ingestion", "🔍 Knowledge Explorer", 
             "🎯 Attack Path Analysis", "🤖 Omni-RAG Intelligence"]
        )

        # Inject Tooltips into the radio buttons via JS for Game-like Hover Explanations
        tooltip_script = """
        <script>
        const tooltips = {
            "🌐 3D Live Dashboard": "Immediate H/W Accelerated 3D node exploration with volumetric bloom and live metrics.",
            "📥 Data Ingestion": "Autonomous pipeline for MITRE STIX, Custom PDFs, and Multi-language YouTube parsing.",
            "🔍 Knowledge Explorer": "Raw semantic table view of database relationships.",
            "🎯 Attack Path Analysis": "Neo4j Dijkstra's algorithm calculating shortest breach paths to critical assets.",
            "🤖 Omni-RAG Intelligence": "Hybrid Vector+Graph reasoning chat powered by local Llama3."
        };
        
        // Wait for Streamlit to render the radio buttons, then inject data attributes
        setTimeout(() => {
            const labels = window.parent.document.querySelectorAll('div[data-testid="stSidebar"] div[role="radiogroup"] label');
            labels.forEach(label => {
                const text = label.innerText;
                if(tooltips[text]) {
                    label.setAttribute('data-tooltip', tooltips[text]);
                }
            });
        }, 1500);
        </script>
        """
        st.components.v1.html(tooltip_script, height=0, width=0)
        
        st.divider()
        
        # Quick Stats
        if st.session_state.neo4j_handler:
            try:
                stats = st.session_state.neo4j_handler.get_graph_stats()
                st.metric("Total Nodes", stats.get("node_count", 0))
                st.metric("Total Relations", stats.get("relationship_count", 0))
            except:
                pass
    
    # Main Content Area
    if page == "🌐 3D Live Dashboard":
        show_dashboard()
    elif page == "📥 Data Ingestion":
        show_ingestion()
    elif page == "🔍 Knowledge Explorer":
        show_exploration()
    elif page == "🎯 Attack Path Analysis":
        show_attack_paths()
    elif page == "🤖 Omni-RAG Intelligence":
        show_rag_interface()

def show_dashboard():
    """Main dashboard view"""
    st.header("📊 System Dashboard")
    
    if not st.session_state.neo4j_handler:
        st.warning("⚠️ Please connect to Neo4j first")
        return
    
    # Get comprehensive stats
    stats = st.session_state.neo4j_handler.get_graph_stats()
    
    st.markdown("""
        <style>
        .hud-metrics {
            background: rgba(15, 23, 42, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="hud-metrics">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Nodes", f"{stats.get('node_count', 0):,}")
        with col2:
            st.metric("Relationships", f"{stats.get('relationship_count', 0):,}")
        with col3:
            st.metric("Node Types", len(stats.get('node_types', {})))
        with col4:
            st.metric("Relation Types", len(stats.get('relationship_types', {})))
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 🛰️ Live Threat Visualizer")
    
    with st.spinner("Initializing CyberGraph Analytics Engine..."):
        try:
            # Force high-limit extraction for the main dashboard background
            graph_data = st.session_state.neo4j_handler.export_for_3d_visualization(limit=800)
            
            with open("advanced_gui.html", "r", encoding="utf-8") as f:
                html_content = f.read()

            html_content = html_content.replace(
                "const graphData = {};",
                f"const graphData = {json.dumps(graph_data)};"
            )
            
            components.html(html_content, height=750, scrolling=False)
            
        except Exception as e:
            st.error(f"Failed to load 3D visualization: {e}")

def show_ingestion():
    """Data ingestion interface"""
    st.header("📥 Data Ingestion")
    
    if not st.session_state.neo4j_handler:
        st.warning("⚠️ Please connect to Neo4j first")
        return
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 MITRE ATT&CK", "📄 PDF Documents", "🎥 YouTube", "🌐 Web URLs"
    ])
    
    with tab1:
        st.subheader("MITRE ATT&CK Framework Ingestion")
        
        matrix_type = st.selectbox(
            "Select ATT&CK Matrix",
            ["enterprise", "mobile", "ics"]
        )
        
        include_deprecated = st.checkbox("Include deprecated objects", value=False)
        
        if st.button("🚀 Start MITRE Ingestion"):
            with st.spinner("Ingesting MITRE ATT&CK data..."):
                try:
                    ingester = MitreAttackIngester(
                        st.session_state.neo4j_handler,
                        matrix=matrix_type
                    )
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    stats = ingester.ingest_all(include_deprecated=include_deprecated)
                    
                    progress_bar.progress(100)
                    status_text.success("✅ Ingestion Complete!")
                    
                    st.json(stats)
                    
                except Exception as e:
                    st.error(f"❌ Ingestion failed: {e}")
    
    with tab2:
        st.subheader("PDF Document Processing")
        
        uploaded_file = st.file_uploader(
            "Upload PDF",
            type=['pdf'],
            accept_multiple_files=False
        )
        
        if uploaded_file and st.button("Process PDF"):
            with st.spinner("Processing PDF..."):
                try:
                    extractor = LLMEntityExtractor(model="llama3")
                    builder = GraphBuilder(st.session_state.neo4j_handler, extractor)
                    pdf_ingester = PDFIngester(
                        st.session_state.neo4j_handler,
                        extractor,
                        builder
                    )
                    
                    result = asyncio.run(pdf_ingester.ingest_file(uploaded_file))
                    
                    st.success(f"✅ Processed: {result['nodes_created']} nodes, {result['relationships_created']} relationships")
                    
                except Exception as e:
                    st.error(f"❌ Processing failed: {e}")
    
    with tab3:
        st.subheader("YouTube Transcript Extraction")
        
        youtube_url = st.text_input("YouTube URL")
        
        if youtube_url and st.button("Extract & Process"):
            with st.spinner("Processing YouTube transcript..."):
                try:
                    extractor = LLMEntityExtractor(model="llama3")
                    builder = GraphBuilder(st.session_state.neo4j_handler, extractor)
                    yt_ingester = YouTubeIngester(
                        st.session_state.neo4j_handler,
                        extractor,
                        builder
                    )
                    
                    result = asyncio.run(yt_ingester.ingest_video(youtube_url))
                    
                    st.success(f"✅ Extracted: {result['nodes_created']} nodes")
                    
                except Exception as e:
                    st.error(f"❌ Extraction failed: {e}")

def show_exploration():
    """Knowledge graph exploration"""
    st.header("🔍 Knowledge Graph Exploration")
    
    if not st.session_state.neo4j_handler:
        st.warning("⚠️ Please connect to Neo4j first")
        return
    
    # Query interface
    query_type = st.selectbox(
        "Query Type",
        ["Find Nodes", "Find Relationships", "Custom Cypher"]
    )
    
    if query_type == "Find Nodes":
        node_type = st.selectbox(
            "Node Type",
            ["Technique", "Tactic", "ThreatGroup", "Malware", "Tool", "CVE"]
        )
        
        limit = st.slider("Max Results", 10, 100, 20)
        
        if st.button("Search"):
            results = st.session_state.neo4j_handler.get_nodes(
                limit=limit,
                node_type=node_type
            )
            
            st.dataframe(results)
    
    elif query_type == "Custom Cypher":
        cypher_query = st.text_area(
            "Cypher Query",
            "MATCH (n) RETURN n LIMIT 25"
        )
        
        if st.button("Execute"):
            try:
                results = st.session_state.neo4j_handler.execute_query(cypher_query)
                st.json(results)
            except Exception as e:
                st.error(f"Query failed: {e}")

def show_attack_paths():
    """Attack path analysis"""
    st.header("🎯 Attack Path Analysis")
    
    if not st.session_state.neo4j_handler:
        st.warning("⚠️ Please connect to Neo4j first")
        return
    
    st.markdown("""
    Analyze potential attack paths between entry points and high-value targets.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        entry_point = st.text_input("Entry Point (e.g., 'Phishing')")
    
    with col2:
        target = st.text_input("Target (e.g., 'Data Exfiltration')")
    
    max_depth = st.slider("Max Path Depth", 1, 10, 5)
    
    if st.button("Find Attack Paths") and entry_point and target:
        with st.spinner("Analyzing attack paths..."):
            try:
                from attack_path_analyzer import AttackPathAnalyzer
                
                analyzer = AttackPathAnalyzer(st.session_state.neo4j_handler)
                paths = analyzer.find_paths(entry_point, target, max_depth)
                
                if paths:
                    st.success(f"Found {len(paths)} attack paths")
                    
                    for i, path in enumerate(paths, 1):
                        st.markdown(f"**Path {i}:** {' → '.join(path)}")
                else:
                    st.warning("No paths found")
                    
            except Exception as e:
                st.error(f"Analysis failed: {e}")

def show_rag_interface():
    """RAG query interface"""
    st.header("🤖 Knowledge Graph RAG Query")
    
    if not st.session_state.neo4j_handler:
        st.warning("⚠️ Please connect to Neo4j first")
        return
    
    st.markdown("""
    Ask questions about cybersecurity threats using natural language.
    The system will retrieve relevant context from the knowledge graph.
    """)
    
    query = st.text_area(
        "Your Question",
        placeholder="What are the common techniques used by APT29?"
    )
    
    retrieval_mode = st.radio(
        "Retrieval Mode",
        ["Hybrid (Vector + Graph)", "Graph Only", "Vector Only"]
    )
    
    if st.button("Submit Query") and query:
        with st.spinner("Generating response..."):
            try:
                from hybrid_retriever import HybridRetriever
                from llm_generator import LLMGenerator
                
                retriever = HybridRetriever(st.session_state.neo4j_handler)
                generator = LLMGenerator()
                
                mode_map = {
                    "Hybrid (Vector + Graph)": "hybrid",
                    "Graph Only": "graph",
                    "Vector Only": "vector"
                }
                
                context = asyncio.run(retriever.retrieve(
                    query,
                    mode=mode_map[retrieval_mode]
                ))
                
                response = asyncio.run(generator.generate(query, context))
                
                st.markdown("### Response")
                st.markdown(response)
                
                with st.expander("View Retrieved Context"):
                    st.json(context)
                    
            except Exception as e:
                st.error(f"Query failed: {e}")

def show_3d_viz():
    """3D visualization interface"""
    st.header("📈 3D Knowledge Graph Visualization")
    
    if not st.session_state.neo4j_handler:
        st.warning("⚠️ Please connect to Neo4j first")
        return
    
    st.markdown("""
    Interactive 3D visualization of the knowledge graph using force-directed layout.
    """)
    
    node_limit = st.slider("Max Nodes", 100, 2000, 500)
    
    node_types = st.multiselect(
        "Filter by Node Types",
        ["Technique", "Tactic", "ThreatGroup", "Malware", "Tool", "CVE"],
        default=None
    )
    
    if st.button("Launch 3D Exploration Environment"):
        with st.spinner("Initializing CyberGraph Analytics Engine..."):
            try:
                graph_data = st.session_state.neo4j_handler.export_for_3d_visualization(
                    limit=node_limit,
                    node_types=node_types if node_types else None
                )
                
                # Load custom UI
                with open("advanced_gui.html", "r", encoding="utf-8") as f:
                    html_content = f.read()

                # Inject JSON directly into the JS logic to avoid CORS or fetch issues inside streamlit IFrame
                json_str = json.dumps(graph_data)
                injected_html = html_content.replace(
                    "fetch('graph_data_3d.json')",
                    f"Promise.resolve({{ json: () => Promise.resolve({json_str}) }})"
                )

                st.success(f"✅ Loaded {len(graph_data['nodes'])} nodes and {len(graph_data['links'])} links.")
                
                # Render embedded full-screen window
                components.html(injected_html, height=850, scrolling=False)
                
            except Exception as e:
                st.error(f"Visualization initialization failed: {e}")

if __name__ == "__main__":
    main()
