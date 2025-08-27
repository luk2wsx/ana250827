import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64

def plot_efficiency_distribution(df):
    """繪製效率分布直方圖"""
    fig = px.histogram(
        df,
        x='效率',
        nbins=20,
        title='效率分布圖',
        labels={'效率': '效率值', 'count': '人數'},
        color_discrete_sequence=['#1f77b4']
    )
    
    fig.add_vline(x=0.8, line_dash="dash", line_color="red", annotation_text="最低要求(80%)")
    fig.add_vline(x=1.05, line_dash="dash", line_color="orange", annotation_text="過高警告(105%)")
    
    fig.update_layout(
        title_x=0.5,
        title_font_size=20,
        xaxis_title="效率值",
        yaxis_title="人數",
        bargap=0.1
    )
    
    return fig

def plot_station_boxplot(df):
    """繪製工站效率箱型圖"""
    fig = px.box(
        df,
        x='工站',
        y='效率',
        title='工站效率分布箱型圖',
        points='all',
        labels={'工站': '工站名稱', '效率': '效率值'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.add_hline(y=0.8, line_dash="dash", line_color="red", annotation_text="最低要求(80%)")
    fig.add_hline(y=1.05, line_dash="dash", line_color="orange", annotation_text="過高警告(105%)")
    
    fig.update_layout(
        title_x=0.5,
        title_font_size=20,
        boxmode='group',
        showlegend=False,
        xaxis=dict(
            tickangle=-45,
            tickfont=dict(size=10),
            automargin=True
        ),
        margin=dict(l=50, r=50, t=50, b=100)
    )
    
    return fig

def plot_ct_scatter(df):
    """繪製標準CT vs 實際CT散點圖"""
    fig = px.scatter(
        df,
        x='標準CT',
        y='實際CT',
        color='工站',
        title='標準CT vs 實際CT對比圖',
        labels={'標準CT': '標準CT時間', '實際CT': '實際CT時間', '工站': '工站'},
        hover_data=['姓名', '效率'],
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    
    max_ct = max(df['標準CT'].max(), df['實際CT'].max())
    fig.add_trace(
        go.Scatter(
            x=[0, max_ct],
            y=[0, max_ct],
            mode='lines',
            name='理想線',
            line=dict(dash='dash', color='gray', width=2)
        )
    )
    
    fig.update_traces(
        marker=dict(size=8, opacity=0.7),
        line=dict(width=2)
    )
    
    fig.update_layout(
        title_x=0.5,
        title_font_size=20,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    return fig

def plot_efficiency_heatmap(df):
    """繪製效率熱力圖"""
    pivot_data = df.pivot_table(
        values='效率',
        index='工站',
        aggfunc='mean'
    )
    
    values = pivot_data.values.flatten()
    text_values = []
    for val in values:
        percentage = val * 100
        text_values.append(f'{percentage:.1f}%')
    
    fig = go.Figure(data=go.Heatmap(
        z=[values],
        x=pivot_data.index,
        y=['平均效率'],
        text=[text_values],
        texttemplate='%{text}',
        textfont={'size': 14},
        colorscale='RdYlGn',
        zmin=0.8,
        zmax=1.05
    ))
    
    fig.update_layout(
        title='工站效率熱力圖',
        title_x=0.5,
        title_font_size=20,
        height=200,
        yaxis_visible=False,
        xaxis_title='工站'
    )
    
    return fig

def plot_top_performers(df):
    """繪製個人效率排名圖"""
    top_performers = df.sort_values('效率', ascending=False).head(10)
    
    fig = px.bar(
        top_performers,
        x='姓名',
        y='效率',
        color='工站',
        title='個人效率排名（前10名）',
        labels={'效率': '效率值', '姓名': '姓名', '工站': '工站'},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    
    fig.update_traces(
        marker=dict(
            line=dict(width=1, color='white'),
            opacity=0.8
        )
    )
    
    fig.update_layout(
        title_x=0.5,
        title_font_size=20,
        xaxis_title="姓名",
        yaxis_title="效率值",
        xaxis=dict(
            tickangle=-45,
            tickfont=dict(size=10),
            automargin=True
        ),
        margin=dict(l=50, r=50, t=50, b=100)
    )
    
    fig.add_hline(y=0.8, line_dash="dash", line_color="red", annotation_text="最低要求(80%)")
    fig.add_hline(y=1.05, line_dash="dash", line_color="orange", annotation_text="過高警告(105%)")
    
    return fig

def generate_complete_html_report(df, station_metrics, top_performers, low_efficiency, high_efficiency, ct_abnormal, efficiency_dist_fig, efficiency_heatmap, station_box_fig, ct_scatter_fig, top_performers_fig):
    """生成包含圖表的完整HTML分析報告"""
    # 修復圖表樣式問題
    # 1. 修復箱型圖的工站名稱顯示問題
    if station_box_fig:
        station_box_fig.update_layout(
            xaxis=dict(
                tickangle=-45,  # 傾斜45度
                tickfont=dict(size=10),
                automargin=True  # 自動調整邊距
            ),
            margin=dict(l=50, r=50, t=50, b=100)  # 增加底部邊距
        )
    
    # 2. 修復散點圖的顏色問題
    if ct_scatter_fig:
        # 確保散點圖有正確的顏色配置
        ct_scatter_fig.update_traces(
            marker=dict(size=8, opacity=0.7),
            line=dict(width=2)
        )
        ct_scatter_fig.update_layout(
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            )
        )
    
    # 3. 修復排名圖的顏色問題
    if top_performers_fig:
        # 確保排名圖有正確的顏色配置
        top_performers_fig.update_traces(
            marker=dict(
                line=dict(width=1, color='white'),
                opacity=0.8
            )
        )
        top_performers_fig.update_layout(
            xaxis=dict(
                tickangle=-45,
                tickfont=dict(size=10),
                automargin=True
            ),
            margin=dict(l=50, r=50, t=50, b=100)
        )
    
    # 將圖表轉換為HTML，使用完整的配置
    efficiency_dist_html = efficiency_dist_fig.to_html(
        include_plotlyjs='cdn', 
        div_id="efficiency_dist",
        config={'displayModeBar': True, 'displaylogo': False}
    )
    efficiency_heatmap_html = efficiency_heatmap.to_html(
        include_plotlyjs=False, 
        div_id="efficiency_heatmap",
        config={'displayModeBar': True, 'displaylogo': False}
    )
    station_box_html = station_box_fig.to_html(
        include_plotlyjs=False, 
        div_id="station_box",
        config={'displayModeBar': True, 'displaylogo': False}
    ) if station_box_fig else ""
    ct_scatter_html = ct_scatter_fig.to_html(
        include_plotlyjs=False, 
        div_id="ct_scatter",
        config={'displayModeBar': True, 'displaylogo': False}
    ) if ct_scatter_fig else ""
    top_performers_html = top_performers_fig.to_html(
        include_plotlyjs=False, 
        div_id="top_performers",
        config={'displayModeBar': True, 'displaylogo': False}
    )
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>工廠生產效率完整分析報告</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #333; padding-bottom: 20px; }
            .section { margin-bottom: 30px; }
            .metric { display: inline-block; margin: 10px; padding: 15px; background-color: #f5f5f5; border-radius: 5px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; font-weight: bold; }
            .alert { color: red; font-weight: bold; }
            .success { color: green; font-weight: bold; }
            .warning { color: orange; font-weight: bold; }
            .chart-container { 
                margin: 20px 0; 
                width: 100%; 
                min-height: 400px;
                overflow-x: auto;
            }
            .chart-title { 
                font-size: 18px; 
                font-weight: bold; 
                margin-bottom: 10px; 
                color: #333;
            }
            .plotly-graph-div {
                width: 100% !important;
                height: 400px !important;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>工廠生產效率完整分析報告</h1>
            <p>生成日期：{{ date }}</p>
        </div>
        
        <div class="section">
            <h2>1. 整體效率指標</h2>
            <div class="metric">平均生產效率：{{ avg_efficiency }}%</div>
            <div class="metric">達標率（≥80%）：{{ qualified_rate }}%</div>
            <div class="metric">最佳工站：{{ best_station }} ({{ best_efficiency }}%)</div>
        </div>

        <div class="section">
            <h2>2. 效率分布圖</h2>
            <div class="chart-container">
                <div class="chart-title">效率分布直方圖</div>
                {{ efficiency_dist_html }}
            </div>
        </div>

        <div class="section">
            <h2>3. 工站效率分析</h2>
            <div class="chart-container">
                <div class="chart-title">工站效率熱力圖</div>
                {{ efficiency_heatmap_html }}
            </div>
            
            <div class="chart-container">
                <div class="chart-title">工站效率分布箱型圖</div>
                {{ station_box_html }}
            </div>
            
            <table>
                <tr>
                    <th>工站</th>
                    <th>平均效率</th>
                    <th>人數</th>
                </tr>
                {% for row in station_metrics.itertuples() %}
                <tr>
                    <td>{{ row.工站 }}</td>
                    <td>{{ "%.1f"|format(row.效率) }}%</td>
                    <td>{{ row.人數 }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>

        {% if ct_scatter_html %}
        <div class="section">
            <h2>4. CT時間分析</h2>
            <div class="chart-container">
                <div class="chart-title">標準CT vs 實際CT對比圖</div>
                {{ ct_scatter_html }}
            </div>
        </div>
        {% endif %}

        <div class="section">
            <h2>5. 個人效率排名</h2>
            <div class="chart-container">
                <div class="chart-title">個人效率排名圖（前10名）</div>
                {{ top_performers_html }}
            </div>
            
            <table>
                <tr>
                    <th>排名</th>
                    <th>工站</th>
                    <th>姓名</th>
                    <th>效率</th>
                </tr>
                {% for row in top_performers.itertuples() %}
                <tr>
                    <td>{{ loop.index }}</td>
                    <td>{{ row.工站 }}</td>
                    <td>{{ row.姓名 }}</td>
                    <td class="success">{{ "%.1f"|format(row.效率*100) }}%</td>
                </tr>
                {% endfor %}
            </table>
        </div>

        <div class="section">
            <h2>6. 效率異常分析</h2>
            {% if low_efficiency|length > 0 %}
            <h3>效率偏低人員 (<80%)</h3>
            <table>
                <tr>
                    <th>工站</th>
                    <th>姓名</th>
                    <th>效率</th>
                </tr>
                {% for row in low_efficiency.itertuples() %}
                <tr>
                    <td>{{ row.工站 }}</td>
                    <td>{{ row.姓名 }}</td>
                    <td class="alert">{{ "%.1f"|format(row.效率*100) }}%</td>
                </tr>
                {% endfor %}
            </table>
            {% endif %}

            {% if high_efficiency|length > 0 %}
            <h3>效率偏高人員 (>105%)</h3>
            <table>
                <tr>
                    <th>工站</th>
                    <th>姓名</th>
                    <th>效率</th>
                </tr>
                {% for row in high_efficiency.itertuples() %}
                <tr>
                    <td>{{ row.工站 }}</td>
                    <td>{{ row.姓名 }}</td>
                    <td class="warning">{{ "%.1f"|format(row.效率*100) }}%</td>
                </tr>
                {% endfor %}
            </table>
            {% endif %}
        </div>

        {% if ct_abnormal|length > 0 %}
        <div class="section">
            <h2>7. CT時間異常分析</h2>
            <table>
                <tr>
                    <th>工站</th>
                    <th>姓名</th>
                    <th>標準CT</th>
                    <th>實際CT</th>
                    <th>CT差異</th>
                    <th>CT差異率</th>
                </tr>
                {% for row in ct_abnormal.itertuples() %}
                <tr>
                    <td>{{ row.工站 }}</td>
                    <td>{{ row.姓名 }}</td>
                    <td>{{ "%.1f"|format(row.標準CT) }}</td>
                    <td>{{ "%.1f"|format(row.實際CT) }}</td>
                    <td>{{ "%.1f"|format(row.CT差異) }}</td>
                    <td class="alert">{{ "%.1f"|format(row.CT差異率) }}%</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endif %}
    </body>
    </html>
    """
    
    from jinja2 import Template
    template_data = {
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'avg_efficiency': f"{df['效率'].mean() * 100:.1f}",
        'qualified_rate': f"{(df['效率'] >= 0.8).mean() * 100:.1f}",
        'best_station': df.groupby('工站')['效率'].mean().idxmax(),
        'best_efficiency': f"{df.groupby('工站')['效率'].mean().max() * 100:.1f}",
        'station_metrics': station_metrics,
        'low_efficiency': low_efficiency,
        'high_efficiency': high_efficiency,
        'ct_abnormal': ct_abnormal,
        'top_performers': top_performers,
        'efficiency_dist_html': efficiency_dist_html,
        'efficiency_heatmap_html': efficiency_heatmap_html,
        'station_box_html': station_box_html,
        'ct_scatter_html': ct_scatter_html,
        'top_performers_html': top_performers_html
    }
    
    template = Template(html_template)
    html_content = template.render(**template_data)
    return html_content

def generate_html_report(df, station_metrics, top_performers, low_efficiency, high_efficiency, ct_abnormal):
    """生成HTML格式的分析報告"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>工廠生產效率分析報告</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #333; padding-bottom: 20px; }
            .section { margin-bottom: 30px; }
            .metric { display: inline-block; margin: 10px; padding: 15px; background-color: #f5f5f5; border-radius: 5px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; font-weight: bold; }
            .alert { color: red; font-weight: bold; }
            .success { color: green; font-weight: bold; }
            .warning { color: orange; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>工廠生產效率分析報告</h1>
            <p>生成日期：{{ date }}</p>
        </div>
        
        <div class="section">
            <h2>1. 整體效率指標</h2>
            <div class="metric">平均生產效率：{{ avg_efficiency }}%</div>
            <div class="metric">達標率（≥80%）：{{ qualified_rate }}%</div>
            <div class="metric">最佳工站：{{ best_station }} ({{ best_efficiency }}%)</div>
        </div>

        <div class="section">
            <h2>2. 工站效率分析</h2>
            <table>
                <tr>
                    <th>工站</th>
                    <th>平均效率</th>
                    <th>人數</th>
                </tr>
                {% for row in station_metrics.itertuples() %}
                <tr>
                    <td>{{ row.工站 }}</td>
                    <td>{{ "%.1f"|format(row.效率) }}%</td>
                    <td>{{ row.人數 }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>

        <div class="section">
            <h2>3. 效率異常分析</h2>
            {% if low_efficiency|length > 0 %}
            <h3>效率偏低人員 (<80%)</h3>
            <table>
                <tr>
                    <th>工站</th>
                    <th>姓名</th>
                    <th>效率</th>
                </tr>
                {% for row in low_efficiency.itertuples() %}
                <tr>
                    <td>{{ row.工站 }}</td>
                    <td>{{ row.姓名 }}</td>
                    <td class="alert">{{ "%.1f"|format(row.效率*100) }}%</td>
                </tr>
                {% endfor %}
            </table>
            {% endif %}

            {% if high_efficiency|length > 0 %}
            <h3>效率偏高人員 (>105%)</h3>
            <table>
                <tr>
                    <th>工站</th>
                    <th>姓名</th>
                    <th>效率</th>
                </tr>
                {% for row in high_efficiency.itertuples() %}
                <tr>
                    <td>{{ row.工站 }}</td>
                    <td>{{ row.姓名 }}</td>
                    <td class="warning">{{ "%.1f"|format(row.效率*100) }}%</td>
                </tr>
                {% endfor %}
            </table>
            {% endif %}
        </div>

        {% if ct_abnormal|length > 0 %}
        <div class="section">
            <h2>4. CT時間異常分析</h2>
            <table>
                <tr>
                    <th>工站</th>
                    <th>姓名</th>
                    <th>標準CT</th>
                    <th>實際CT</th>
                    <th>CT差異</th>
                    <th>CT差異率</th>
                </tr>
                {% for row in ct_abnormal.itertuples() %}
                <tr>
                    <td>{{ row.工站 }}</td>
                    <td>{{ row.姓名 }}</td>
                    <td>{{ "%.1f"|format(row.標準CT) }}</td>
                    <td>{{ "%.1f"|format(row.實際CT) }}</td>
                    <td>{{ "%.1f"|format(row.CT差異) }}</td>
                    <td class="alert">{{ "%.1f"|format(row.CT差異率) }}%</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endif %}

        <div class="section">
            <h2>5. 個人效率排名（前10名）</h2>
            <table>
                <tr>
                    <th>排名</th>
                    <th>工站</th>
                    <th>姓名</th>
                    <th>效率</th>
                </tr>
                {% for row in top_performers.itertuples() %}
                <tr>
                    <td>{{ loop.index }}</td>
                    <td>{{ row.工站 }}</td>
                    <td>{{ row.姓名 }}</td>
                    <td class="success">{{ "%.1f"|format(row.效率*100) }}%</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    """
    
    from jinja2 import Template
    template_data = {
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'avg_efficiency': f"{df['效率'].mean() * 100:.1f}",
        'qualified_rate': f"{(df['效率'] >= 0.8).mean() * 100:.1f}",
        'best_station': df.groupby('工站')['效率'].mean().idxmax(),
        'best_efficiency': f"{df.groupby('工站')['效率'].mean().max() * 100:.1f}",
        'station_metrics': station_metrics,
        'low_efficiency': low_efficiency,
        'high_efficiency': high_efficiency,
        'ct_abnormal': ct_abnormal,
        'top_performers': top_performers
    }
    
    template = Template(html_template)
    html_content = template.render(**template_data)
    return html_content

def main():
    st.title("廠長效率分析系統 - Excel檔案合併工具")
    st.write("請選擇兩個Excel檔案進行合併，系統會根據料號和工序欄位進行比對，並計算效率分析")
    
    # 檔案上傳區域
    st.header("📁 檔案上傳")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("第一個Excel檔案 (匯入標準CT)")
        file1 = st.file_uploader("選擇料號工序Excel檔案", type=['xlsx', 'xls'], key="file1")
        
    with col2:
        st.subheader("第二個Excel檔案 (匯入員工績效明細表)")
        file2 = st.file_uploader("選擇員工績效明細Excel檔案", type=['xlsx', 'xls'], key="file2")
    
    if file1 is not None and file2 is not None:
        try:
            # 讀取Excel檔案
            df1 = pd.read_excel(file1)
            df2 = pd.read_excel(file2)
            
            # 欄位名稱統一與清理
            st.header("🔄 欄位名稱處理")
            
            # 檢查並重命名欄位
            rename_mapping_1 = {}
            rename_mapping_2 = {}
            
            # 第一個檔案的欄位重命名
            if '作業時間' in df1.columns:
                rename_mapping_1['作業時間'] = '標工'
            if '工作內容' in df1.columns:
                rename_mapping_1['工作內容'] = '工站'
                
            # 第二個檔案的欄位重命名
            if '產出' in df2.columns:
                rename_mapping_2['產出'] = '實際產出'
            if 'RUN總時數' in df2.columns:
                rename_mapping_2['RUN總時數'] = '人員作業時間'
                
            if rename_mapping_1:
                df1.rename(columns=rename_mapping_1, inplace=True)
                st.write(f"檔案1欄位重命名: {rename_mapping_1}")
                
            if rename_mapping_2:
                df2.rename(columns=rename_mapping_2, inplace=True)
                st.write(f"檔案2欄位重命名: {rename_mapping_2}")
            
            st.success("✅ 檔案讀取成功！")
            
            # 顯示檔案資訊
            st.header("📊 檔案資訊")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("第一個檔案")
                st.write(f"行數: {len(df1)}")
                st.write(f"欄位: {list(df1.columns)}")
                st.dataframe(df1.head())
                
            with col2:
                st.subheader("第二個檔案")
                st.write(f"行數: {len(df2)}")
                st.write(f"欄位: {list(df2.columns)}")
                st.dataframe(df2.head())
            
            # 選擇合併欄位
            st.header("🔗 合併設定")
            
            # 檢查是否有料號和工序欄位
            common_columns = list(set(df1.columns) & set(df2.columns))
            st.write(f"兩個檔案共有的欄位: {common_columns}")
            
            # 讓使用者選擇合併欄位
            merge_columns = st.multiselect(
                "選擇要用於合併的欄位（建議選擇料號和工序）",
                common_columns,
                default=common_columns[:2] if len(common_columns) >= 2 else common_columns
            )
            
            if len(merge_columns) >= 1:
                st.write(f"選擇的合併欄位: {merge_columns}")
                
                # 處理空白格變為NaN
                st.header("🔄 資料處理")
                
                # 將空白格變為NaN
                df1_processed = df1.replace('', np.nan)
                df2_processed = df2.replace('', np.nan)
                
                # 去除空白與統一格式
                for col in ['料號', '工序']:
                    if col in df1_processed.columns:
                        df1_processed[col] = df1_processed[col].astype(str).str.strip()
                    if col in df2_processed.columns:
                        df2_processed[col] = df2_processed[col].astype(str).str.strip()
                
                # 過濾掉NaN資料
                df1_filtered = df1_processed.dropna(subset=merge_columns)
                df2_filtered = df2_processed.dropna(subset=merge_columns)
                
                st.write(f"處理前 - 檔案1: {len(df1)} 行, 檔案2: {len(df2)} 行")
                st.write(f"處理後 - 檔案1: {len(df1_filtered)} 行, 檔案2: {len(df2_filtered)} 行")
                
                # 合併資料
                st.header("🔗 資料合併")
                
                # 選擇合併方式
                merge_method = st.selectbox(
                    "選擇合併方式",
                    ["inner", "left", "right", "outer"],
                    help="inner: 只保留兩個檔案都有的記錄\nleft: 保留左邊檔案的所有記錄\nright: 保留右邊檔案的所有記錄\nouter: 保留所有記錄"
                )
                
                if st.button("開始合併與分析") or 'analysis_completed' in st.session_state:
                    try:
                        # 執行合併
                        merged_df = pd.merge(
                            df1_filtered, 
                            df2_filtered, 
                            on=merge_columns, 
                            how=merge_method,
                            suffixes=('_檔案1', '_檔案2')
                        )
                        
                        st.success(f"✅ 合併完成！合併後共有 {len(merged_df)} 行資料")
                        
                        # 將結果存儲到session state
                        st.session_state['merged_df'] = merged_df
                        st.session_state['df1_filtered'] = df1_filtered
                        st.session_state['df2_filtered'] = df2_filtered
                        st.session_state['merge_columns'] = merge_columns
                        
                        # 效率分析計算
                        st.header("📊 效率分析計算")
                        
                        # 標準CT 改名
                        if '標工' in merged_df.columns:
                            merged_df.rename(columns={'標工': '標準CT'}, inplace=True)
                        
                        # 計算欄位
                        if all(col in merged_df.columns for col in ['人員作業時間', '實際產出']):
                            merged_df['實際CT'] = (merged_df['人員作業時間'] * 3600) / merged_df['實際產出']
                        
                        if all(col in merged_df.columns for col in ['實際產出', '理論產出']):
                            merged_df['效率'] = merged_df['實際產出'] / merged_df['理論產出']
                            merged_df['效率'] = (merged_df['效率'] * 100).round(2).astype(str) + '%'
                        
                        # 選取重要欄位
                        important_columns = ['工站', '姓名', '人員作業時間', '理論產出', '實際產出', '效率', '標準CT', '實際CT']
                        available_columns = [col for col in important_columns if col in merged_df.columns]
                        
                        if available_columns:
                            selected_df = merged_df[available_columns].copy()
                            
                            # 數值欄位轉換
                            if '實際產出' in selected_df.columns:
                                selected_df['實際產出'] = pd.to_numeric(selected_df['實際產出'], errors='coerce')
                            if '實際CT' in selected_df.columns:
                                selected_df['實際CT'] = pd.to_numeric(selected_df['實際CT'], errors='coerce')
                            if '效率' in selected_df.columns:
                                selected_df['效率值'] = pd.to_numeric(selected_df['效率'].str.replace('%', ''), errors='coerce')
                            
                            # 將空白字串轉為 NaN
                            for col in ['姓名', '工站', '標準CT']:
                                if col in selected_df.columns:
                                    selected_df[col] = selected_df[col].replace(r'^\s*$', np.nan, regex=True)
                            
                            # 過濾資料（排除負值或缺失）
                            filter_conditions = []
                            
                            if '人員作業時間' in selected_df.columns:
                                filter_conditions.append(selected_df['人員作業時間'].fillna(0) >= 0.03)
                            if '實際產出' in selected_df.columns:
                                filter_conditions.append(selected_df['實際產出'].fillna(0) >= 0)
                            if '實際CT' in selected_df.columns:
                                filter_conditions.append(selected_df['實際CT'].fillna(0) >= 0)
                            if '效率' in selected_df.columns:
                                filter_conditions.append(~selected_df['效率'].isin(['0.0%', 'inf%', 'nan%']))
                            if '姓名' in selected_df.columns:
                                filter_conditions.append(~selected_df['姓名'].isin(['MFGR', 'MFG_R']))
                            if '效率值' in selected_df.columns:
                                filter_conditions.append(selected_df['效率值'].between(20, 150))
                            if '工站' in selected_df.columns:
                                filter_conditions.append(selected_df['工站'].notna())
                            if '標準CT' in selected_df.columns:
                                filter_conditions.append(selected_df['標準CT'].notna())
                            if '姓名' in selected_df.columns:
                                filter_conditions.append(selected_df['姓名'].notna())
                            
                            if filter_conditions:
                                filtered_df = selected_df[np.logical_and.reduce(filter_conditions)]
                                st.success(f"✅ 過濾完成！過濾後共有 {len(filtered_df)} 行資料")
                                
                                # 存儲過濾後的結果到session state
                                st.session_state['filtered_df'] = filtered_df
                                st.session_state['analysis_completed'] = True
                                
                                # 顯示過濾後的結果
                                st.header("📋 效率分析結果")
                                st.dataframe(filtered_df)
                                
                                # 統計資訊
                                st.header("📈 效率統計")
                                if '效率值' in filtered_df.columns:
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("平均效率", f"{filtered_df['效率值'].mean():.2f}%")
                                    with col2:
                                        st.metric("最高效率", f"{filtered_df['效率值'].max():.2f}%")
                                    with col3:
                                        st.metric("最低效率", f"{filtered_df['效率值'].min():.2f}%")
                                    with col4:
                                        st.metric("效率標準差", f"{filtered_df['效率值'].std():.2f}%")
                            else:
                                filtered_df = selected_df
                                st.session_state['filtered_df'] = filtered_df
                                st.session_state['analysis_completed'] = True
                                st.warning("⚠️ 無法進行資料過濾，顯示原始資料")
                        else:
                            filtered_df = merged_df
                            st.session_state['filtered_df'] = filtered_df
                            st.session_state['analysis_completed'] = True
                            st.warning("⚠️ 無法找到效率分析所需欄位，顯示合併結果")
                        
                        # 顯示合併結果
                        st.header("📋 完整合併結果")
                        st.dataframe(merged_df)
                        
                        # 下載按鈕
                        st.header("💾 下載結果")
                        
                        # 創建下載連結
                        st.header("💾 下載結果")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # 下載完整合併結果
                            output_full = BytesIO()
                            merged_df.to_csv(output_full, index=False, encoding='utf-8-sig')
                            output_full.seek(0)
                            
                            st.download_button(
                                label="📥 下載完整合併結果",
                                data=output_full.getvalue(),
                                file_name="完整合併結果.csv",
                                mime="text/csv"
                            )
                        
                        with col2:
                            # 下載效率分析結果
                            if 'filtered_df' in locals():
                                output_filtered = BytesIO()
                                filtered_df.to_csv(output_filtered, index=False, encoding='utf-8-sig')
                                output_filtered.seek(0)
                                
                                st.download_button(
                                    label="📥 下載效率分析結果",
                                    data=output_filtered.getvalue(),
                                    file_name="效率分析結果.csv",
                                    mime="text/csv"
                                )
                            else:
                                st.info("無效率分析結果可下載")
                        
                        # 顯示統計資訊
                        st.header("📈 處理統計")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("原始檔案1行數", len(df1))
                            st.metric("處理後檔案1行數", len(df1_filtered))
                            
                        with col2:
                            st.metric("原始檔案2行數", len(df2))
                            st.metric("處理後檔案2行數", len(df2_filtered))
                            
                        with col3:
                            st.metric("合併後行數", len(merged_df))
                            st.metric("合併欄位數", len(merge_columns))
                            
                        with col4:
                            if 'filtered_df' in locals():
                                st.metric("效率分析行數", len(filtered_df))
                                st.metric("過濾率", f"{((len(merged_df) - len(filtered_df)) / len(merged_df) * 100):.1f}%")
                            else:
                                st.metric("效率分析行數", "N/A")
                                st.metric("過濾率", "N/A")
                        
                        # 進階分析（依據 de_250827-02 規則完整版）
                        st.header("🧠 進階分析")
                        try:
                            # 準備分析資料來源（優先使用session state）
                            if 'filtered_df' in st.session_state:
                                base_df = st.session_state['filtered_df'].copy()
                            elif 'merged_df' in st.session_state:
                                base_df = st.session_state['merged_df'].copy()
                            elif 'filtered_df' in locals():
                                base_df = filtered_df.copy()
                            elif 'selected_df' in locals():
                                base_df = selected_df.copy()
                            else:
                                base_df = merged_df.copy()
                            
                            # 檢查必要欄位是否存在
                            needed_cols = ['工站', '姓名']
                            has_ct_cols = all(col in base_df.columns for col in ['標準CT', '實際CT'])
                            has_eff_cols = ('效率值' in base_df.columns) or ('效率' in base_df.columns)
                            if all(col in base_df.columns for col in needed_cols) and has_eff_cols:
                                analysis_df = base_df.copy()
                                
                                # 效率數值化 -> 小數(0~1)
                                if '效率值' in analysis_df.columns:
                                    analysis_df['效率'] = pd.to_numeric(analysis_df['效率值'], errors='coerce') / 100.0
                                else:
                                    analysis_df['效率'] = pd.to_numeric(analysis_df['效率'].astype(str).str.replace('%',''), errors='coerce') / 100.0
                                
                                # CT數值化與差異
                                if has_ct_cols:
                                    analysis_df['標準CT'] = pd.to_numeric(analysis_df['標準CT'], errors='coerce')
                                    analysis_df['實際CT'] = pd.to_numeric(analysis_df['實際CT'], errors='coerce')
                                    analysis_df['CT差異'] = analysis_df['實際CT'] - analysis_df['標準CT']
                                    analysis_df['CT差異率'] = (analysis_df['CT差異'] / analysis_df['標準CT'] * 100)
                                
                                # 工站效率指標
                                station_metrics = analysis_df.groupby('工站').agg({
                                    '效率': 'mean',
                                    '姓名': 'count'
                                }).reset_index().rename(columns={'姓名': '人數'})
                                station_metrics['效率'] = station_metrics['效率'] * 100.0
                                
                                # 效率異常分群
                                too_low = 0.8
                                too_high = 1.05
                                low_efficiency = analysis_df[analysis_df['效率'] < too_low].copy()
                                high_efficiency = analysis_df[analysis_df['效率'] > too_high].copy()
                                
                                # 個人效率前10
                                top_performers = analysis_df.sort_values('效率', ascending=False).head(10).copy()
                                
                                # CT異常（若有CT欄位）
                                if has_ct_cols:
                                    ct_abnormal = analysis_df[analysis_df['CT差異率'].abs() > 20].copy()
                                else:
                                    ct_abnormal = pd.DataFrame(columns=['工站','姓名','標準CT','實際CT','CT差異','CT差異率'])
                                
                                # 顯示重點數據
                                col_a, col_b, col_c = st.columns(3)
                                with col_a:
                                    st.metric("平均效率", f"{analysis_df['效率'].mean()*100:.1f}%")
                                with col_b:
                                    st.metric("達標率(≥80%)", f"{(analysis_df['效率']>=0.8).mean()*100:.1f}%")
                                with col_c:
                                    st.metric("工站數", station_metrics['工站'].nunique())
                                
                                # 詳細分析圖表
                                st.subheader("📊 詳細分析圖表")
                                
                                # 1. 效率分布圖
                                st.markdown("#### 1. 效率分布圖")
                                efficiency_dist_fig = plot_efficiency_distribution(analysis_df)
                                st.plotly_chart(efficiency_dist_fig, use_container_width=True)
                                
                                # 2. 工站效率熱力圖
                                st.markdown("#### 2. 工站效率熱力圖")
                                efficiency_heatmap = plot_efficiency_heatmap(analysis_df)
                                st.plotly_chart(efficiency_heatmap, use_container_width=True)
                                
                                # 3. 工站效率箱型圖
                                st.markdown("#### 3. 工站效率分布箱型圖")
                                station_box_fig = plot_station_boxplot(analysis_df)
                                st.plotly_chart(station_box_fig, use_container_width=True)
                                
                                # 4. CT時間分析（如果有CT數據）
                                if has_ct_cols:
                                    st.markdown("#### 4. CT時間分析")
                                    ct_scatter_fig = plot_ct_scatter(analysis_df)
                                    st.plotly_chart(ct_scatter_fig, use_container_width=True)
                                
                                # 5. 個人效率排名圖
                                st.markdown("#### 5. 個人效率排名圖")
                                top_performers_fig = plot_top_performers(analysis_df)
                                st.plotly_chart(top_performers_fig, use_container_width=True)
                                
                                # 數據表格顯示
                                st.subheader("📋 詳細數據分析")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown("##### 工站效率指標")
                                    st.dataframe(station_metrics)
                                    
                                    st.markdown("##### 效率偏低(<80%)")
                                    if len(low_efficiency) > 0:
                                        st.dataframe(low_efficiency[['工站','姓名','效率']])
                                    else:
                                        st.info("無效率偏低人員")
                                
                                with col2:
                                    st.markdown("##### 效率偏高(>105%)")
                                    if len(high_efficiency) > 0:
                                        st.dataframe(high_efficiency[['工站','姓名','效率']])
                                    else:
                                        st.info("無效率偏高人員")
                                    
                                    st.markdown("##### 個人效率前10")
                                    st.dataframe(top_performers[['工站','姓名','效率']])
                                
                                if has_ct_cols and len(ct_abnormal) > 0:
                                    st.markdown("##### CT時間異常(|差異率|>20%)")
                                    st.dataframe(ct_abnormal[['工站','姓名','標準CT','實際CT','CT差異','CT差異率']])
                                
                                # 下載進階分析結果
                                st.header("📥 下載進階分析結果")
                                
                                # 生成HTML報告
                                html_report = generate_html_report(
                                    analysis_df, station_metrics, top_performers, 
                                    low_efficiency, high_efficiency, ct_abnormal
                                )
                                
                                # 生成完整HTML報告（包含圖表）
                                complete_html_report = generate_complete_html_report(
                                    analysis_df, station_metrics, top_performers, 
                                    low_efficiency, high_efficiency, ct_abnormal,
                                    efficiency_dist_fig, efficiency_heatmap, station_box_fig, 
                                    ct_scatter_fig if has_ct_cols else None, top_performers_fig
                                )
                                
                                # 下載按鈕區域
                                st.markdown("### 📊 完整分析報告")
                                dcol1, dcol2 = st.columns(2)
                                with dcol1:
                                    # 完整HTML報告下載（包含圖表）
                                    st.download_button(
                                        "📑 下載完整分析報告（含圖表）", 
                                        complete_html_report, 
                                        "工廠生產效率完整分析報告.html", 
                                        "text/html",
                                        help="包含所有圖表和數據分析的完整報告"
                                    )
                                with dcol2:
                                    # 基本HTML報告下載
                                    st.download_button(
                                        "📄 下載基本分析報告", 
                                        html_report, 
                                        "工廠生產效率分析報告.html", 
                                        "text/html",
                                        help="僅包含數據表格的基本報告"
                                    )
                                
                                st.markdown("### 📋 個別數據下載")
                                dcol3, dcol4, dcol5 = st.columns(3)
                                with dcol3:
                                    buf = BytesIO(); analysis_df.to_csv(buf, index=False, encoding='utf-8-sig'); buf.seek(0)
                                    st.download_button("下載進階分析基礎資料", buf.getvalue(), "進階分析_基礎資料.csv", "text/csv")
                                with dcol4:
                                    buf = BytesIO(); station_metrics.to_csv(buf, index=False, encoding='utf-8-sig'); buf.seek(0)
                                    st.download_button("下載工站效率指標", buf.getvalue(), "進階分析_工站效率指標.csv", "text/csv")
                                with dcol5:
                                    buf = BytesIO(); top_performers.to_csv(buf, index=False, encoding='utf-8-sig'); buf.seek(0)
                                    st.download_button("下載個人效率前10", buf.getvalue(), "進階分析_個人前10.csv", "text/csv")
                                
                                dcol6, dcol7, dcol8 = st.columns(3)
                                with dcol6:
                                    buf = BytesIO(); low_efficiency.to_csv(buf, index=False, encoding='utf-8-sig'); buf.seek(0)
                                    st.download_button("下載效率偏低清單", buf.getvalue(), "進階分析_效率偏低.csv", "text/csv")
                                with dcol7:
                                    buf = BytesIO(); high_efficiency.to_csv(buf, index=False, encoding='utf-8-sig'); buf.seek(0)
                                    st.download_button("下載效率偏高清單", buf.getvalue(), "進階分析_效率偏高.csv", "text/csv")
                                with dcol8:
                                    if has_ct_cols and len(ct_abnormal) > 0:
                                        buf = BytesIO(); ct_abnormal.to_csv(buf, index=False, encoding='utf-8-sig'); buf.seek(0)
                                        st.download_button("下載CT異常清單", buf.getvalue(), "進階分析_CT異常.csv", "text/csv")
                                    else:
                                        st.info("無CT異常數據")
                                
                                # 專業改善建議
                                st.header("💡 專業改善建議")
                                with st.expander("點擊查看詳細改善建議"):
                                    # 工站效率異常分析
                                    high_stations = analysis_df[analysis_df['效率'] > too_high]['工站'].unique()
                                    low_stations = analysis_df[analysis_df['效率'] < too_low]['工站'].unique()
                                    
                                    if len(high_stations) > 0:
                                        st.warning(f"""
                                        ### ⚠️ 標準工時定義過鬆的工站（{len(high_stations)}個）：
                                        
                                        #### 影響工站：{', '.join(high_stations)}
                                        
                                        #### 建議措施：
                                        1. **重新評估標準工時的合理性**
                                        2. **分析高效率人員的作業方法**
                                        3. **工時平衡與人力配置**
                                        """)
                                    
                                    if len(low_stations) > 0:
                                        st.error(f"""
                                        ### 🔧 需要製程改善的工站（{len(low_stations)}個）：
                                        
                                        #### 影響工站：{', '.join(low_stations)}
                                        
                                        #### 改善方向：
                                        1. **製程分析與改善**
                                        2. **工具與設備改善**
                                        3. **作業環境優化**
                                        4. **標準作業優化**
                                        """)
                                    
                                    if len(low_efficiency) > 0:
                                        st.info(f"""
                                        ### 👥 人員效率改善建議（{len(low_efficiency)}人）：
                                        
                                        #### 1. 技能提升計劃
                                        - 專業培訓
                                        - 經驗分享
                                        
                                        #### 2. 工作支援系統
                                        - 工具支援
                                        - 環境支援
                                        
                                        #### 3. 改善追蹤機制
                                        - 目標管理
                                        - 激勵機制
                                        """)
                            else:
                                st.info("進階分析略過：缺少必要欄位（至少需含 工站/姓名/效率）")
                        except Exception as e:
                            st.warning(f"進階分析發生錯誤：{str(e)}")
                        
                    except Exception as e:
                        st.error(f"❌ 合併過程中發生錯誤: {str(e)}")
                        st.write("請檢查選擇的合併欄位是否正確")
            else:
                st.warning("⚠️ 請至少選擇一個合併欄位")
                
        except Exception as e:
            st.error(f"❌ 檔案讀取錯誤: {str(e)}")
            st.write("請確認上傳的檔案是有效的Excel檔案")
    
    else:
        st.info("ℹ️ 請上傳兩個Excel檔案以開始合併程序")
    
    # 使用說明
    with st.expander("📖 使用說明"):
        st.write("""
        ### 使用步驟：
        1. **上傳檔案**: 
           - 第一個檔案：工時資料（包含料號、工序、作業時間、工作內容等）
           - 第二個檔案：標準工時資料（包含料號、工序、產出、RUN總時數等）
        2. **選擇合併欄位**: 選擇兩個檔案都有的欄位作為合併依據（通常是料號和工序）
        3. **選擇合併方式**: 
           - inner: 只保留兩個檔案都有的記錄
           - left: 保留左邊檔案的所有記錄
           - right: 保留右邊檔案的所有記錄
           - outer: 保留所有記錄
        4. **開始合併與分析**: 點擊按鈕開始合併和效率分析程序
        5. **下載結果**: 下載完整合併結果和效率分析結果
        
        ### 自動處理功能：
        - **欄位重命名**: 自動將「作業時間」→「標工」、「工作內容」→「工站」、「產出」→「實際產出」、「RUN總時數」→「人員作業時間」
        - **資料清理**: 自動去除空白並統一格式
        - **效率計算**: 自動計算實際CT和效率百分比
        - **資料過濾**: 自動過濾無效資料（效率20%-150%、排除特定人員等）
        
        ### 注意事項：
        - 系統會自動將空白格轉換為NaN並過濾掉
        - 合併欄位必須在兩個檔案中都存在
        - 建議使用料號和工序作為合併欄位
        - 效率分析會自動過濾異常資料
        """)

if __name__ == "__main__":
    main()
