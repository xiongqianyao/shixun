import jieba
import pandas as pd
import streamlit as st
import requests
from bs4 import BeautifulSoup
from collections import Counter
from pyecharts.charts import Pie, Bar, Line, Scatter, Radar, Boxplot, Funnel
from pyecharts.charts import WordCloud as PyechartsWordCloud
from pyecharts import options as opts


# 抓取并处理文章内容
def getcontent(url_input):
    response = requests.get(url_input)
    encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else None
    soup = BeautifulSoup(response.content, 'html.parser', from_encoding=encoding)
    text = soup.text
    # 获取网站文本内容
    # 使用 jieba 库进行中文分词处理
    words = [word for word in jieba.cut(text) if len(word) >= 2 and '\u4e00' <= word <= '\u9fff']
    # 统计词频
    word_counts = Counter(words)
    return word_counts


# 创建词云图
def create_wordcloud(word_counts):
    words = list(word_counts.keys())
    values = list(word_counts.values())

    c = (
        PyechartsWordCloud()
            .add("", zip(words, values), word_size_range=[20, 100], shape="circle")
            .set_global_opts(title_opts=opts.TitleOpts(title="词云图"))
            .render("wordcloud.html")
    )
    st.components.v1.html(open('wordcloud.html', 'r', encoding='utf-8').read(), height=600)


# 绘制饼状图
def plot_pie_chart(word_counts):
    pie_chart = (
        Pie().add("", word_counts.most_common(20))
            # .set_global_opts(title_opts=opts.TitleOpts(title="词频饼状图"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
            .render("pie_chart.html")
    )
    st.components.v1.html(open('pie_chart.html', 'r', encoding='utf-8').read(), height=600)


# 绘制条形图
def plot_bar_chart(word_counts):
    bar_chart = (
        Bar().add_xaxis([word for word, count in word_counts.most_common(20)])
            .add_yaxis("词频", [count for word, count in word_counts.most_common(20)])
            .set_global_opts(title_opts=opts.TitleOpts(title="词频条形图"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
            .render("bar_chart.html")
    )
    st.components.v1.html(open('bar_chart.html', 'r', encoding='utf-8').read(), height=600)


# 绘制折线图
def plot_line_chart(word_counts):
    line_chart = (
        Line().add_xaxis([word for word, count in word_counts.most_common(20)])
            .add_yaxis("词频", [count for word, count in word_counts.most_common(20)])
            .set_global_opts(title_opts=opts.TitleOpts(title="词频折线图"))
            # .set_series_opts(label_opts=opts.LabelOpts(formatter="{c}"))
            .render("line_chart.html")
    )
    st.components.v1.html(open('line_chart.html', 'r', encoding='utf-8').read(), height=600)


# 创建散点图
def create_scatter_chart(word_counts):
    c = (
        Scatter()
            .add_xaxis([word for word, count in word_counts.most_common(20)])
            .add_yaxis("散点值", [count for word, count in word_counts.most_common(20)])
            # .set_series_opts(label_opts=opts.LabelOpts(formatter="{c}"))
            .set_global_opts(
            title_opts=opts.TitleOpts(title="散点图"),
            # xaxis_opts=opts.AxisOpts(type_="category"),
        )
            .render("scatter_chart.html")
    )
    st.components.v1.html(open('scatter_chart.html', 'r', encoding='utf-8').read(), height=600)


# 生成雷达图
def generate_radar_chart(word_counts):
    words = [word for word, count in word_counts.most_common(20)]
    values = [count for word, count in word_counts.most_common(20)]

    c = (
        Radar()
            .add_schema(schema=[
            opts.RadarIndicatorItem(name=word, max_=15) for word in words
        ])
            .add("中文字典雷达图", [values], areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .render("radar_chart.html")
    )
    st.components.v1.html(open('radar_chart.html', 'r', encoding='utf-8').read(), height=600)


#漏斗图
def funnel_from_dict(data_dict):
    # 转换中文词典为 DataFrame
    df = pd.DataFrame((list(data_dict.items())[:20]), columns=['Category', 'Values'])
    # 创建漏斗图
    funnel_chart = (
        Funnel()
            .add(
            series_name="Funnel",
            data_pair=df.values.tolist(),
            label_opts=opts.LabelOpts(position="inside"),
        )
            .render("funnel_chart.html")
    )
    st.components.v1.html(open('funnel_chart.html', 'r', encoding='utf-8').read(), height=600)


def main():
    st.title("爬虫可视化应用")
    # 输入网址
    url = st.text_input("请输入要爬取的网址：")
    # 选择图表类型
    chart_type = st.radio("选择图表类型", ["饼状图", "条形图", "折线图", "词云图", "散点图", "雷达图", "漏斗图"])

    # 爬取网页内容
    if st.button("爬取"):
        if url:
            # 分析文本内容
            word_counts = getcontent(url)

            # 显示相应的图表
            if chart_type == "饼状图":
                plot_pie_chart(word_counts)
            elif chart_type == "条形图":
                plot_bar_chart(word_counts)
            elif chart_type == "折线图":
                plot_line_chart(word_counts)
            elif chart_type == '词云图':
                create_wordcloud(word_counts)
            elif chart_type == '散点图':
                create_scatter_chart(word_counts)
            elif chart_type == '雷达图':
                generate_radar_chart(word_counts)
            elif chart_type == '漏斗图':
                funnel_from_dict(word_counts)
            else:
                st.warning("请输入要爬取的网址！")


# 运行 Streamlit 应用程序
if __name__ == "__main__":
    main()
