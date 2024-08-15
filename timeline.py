import json
import argparse
import plotly.graph_objects as go
from datetime import datetime
import plotly.io as pio
import plotly.colors as pc

def createTimeline(json_path:str,img_save:bool=True,img_show:bool=True,html_save:bool=False):
    DEFAULT_SETTINGS={
        "now":datetime.now()
    }
    DEFAULT_LAYOUT_DICT={
        "title":"Timeline",
        "xaxis_title":"Time",
        "yaxis_title":"Series",
        "yaxis_showticklabels":True,
        "showlegend":True
    }
    DEFAULT_OUT_IMG_DICT={
        "path":"timeline.png",
        "width":1200,
        "height":600,
        "scale":1
    }
    DEFAULT_SERIES_INFO={
        "intervals":[],
        "color":"",
        "bgcolor":"rgba(255, 255, 255, 0.7)"
    }
    DEFAULT_INTERVAL={
        "description":"",
        "width":1
    }
    
    with open(json_path,mode="r",encoding="utf-8") as f:
        data=json.load(f)

    settings=data.get("settings",DEFAULT_SETTINGS)
    layout_settings=data.get("layout",DEFAULT_LAYOUT_DICT)
    series_data=data.get("data",{})
    out_img_settings=data.get("out_img",DEFAULT_OUT_IMG_DICT)

    fig=go.Figure()
    annotations=[]

    y_position=0

    def checkOverlap(intervals):
        sorted_intervals=sorted(intervals,key=lambda x:x["start"])
        for i in range(len(sorted_intervals)-1):
            if(sorted_intervals[i]["end"]>sorted_intervals[i+1]["start"]):
                print(f"Warning : Overlapping intervals detected in series")

    for i,(series,series_info) in enumerate(series_data.items()):
        intervals=series_info.get("intervals",DEFAULT_SERIES_INFO["intervals"])
        color=series_info.get("color",DEFAULT_SERIES_INFO["color"])
        bgcolor=series_info.get("bgcolor",DEFAULT_SERIES_INFO["bgcolor"])
        
        if(intervals!=None):

            checkOverlap(intervals)
                
            fig_text_list=[]
                
            for interval in intervals:
                if("start" in interval and "end" in interval):

                    start=datetime.strptime(interval["start"],"%Y-%m-%d")
                    if(interval["end"]=="now"):
                        end=settings.get("now",DEFAULT_SETTINGS["now"])
                    else:
                        end=datetime.strptime(interval["end"],"%Y-%m-%d")
                    description=interval.get("description",DEFAULT_INTERVAL["description"])
                    width=interval.get("width",DEFAULT_INTERVAL["width"])
                    
                    if(color==""):
                        color=pc.DEFAULT_PLOTLY_COLORS[i%len(pc.DEFAULT_PLOTLY_COLORS)]

                    fig_text=f"{series}:{description}" if description!="" else series
                    line_dict=dict(width=20*width,color=color)

                    fig.add_trace(go.Scatter(
                        x=[start,end],
                        y=[y_position,y_position],
                        mode="lines",
                        line=line_dict,
                        name=series,
                        hoverinfo="text"
                    ))

                    if(fig_text not in fig_text_list):
                        annotations.append(dict(
                            x=start,
                            y=y_position,
                            xref="x",
                            yref="y",
                            text=fig_text,
                            showarrow=False,
                            font=dict(
                                color="black",
                                size=12,
                                family="Arial"
                            ),
                            align="left",
                            bgcolor=bgcolor,
                            xanchor="left",
                            ax=1000,
                            ay=0
                        ))
                        fig_text_list.append(fig_text)
                else:
                    print(f"error : not start or end flag => seriesName = \"{series}\" ,  content = \"{interval}\"")


            y_position+=1

    fig.update_layout(
        title=layout_settings.get("title",DEFAULT_LAYOUT_DICT["title"]),
        xaxis_title=layout_settings.get("xaxis_title",DEFAULT_LAYOUT_DICT["xaxis_title"]),
        yaxis=dict(
            title=layout_settings.get("yaxis_title",DEFAULT_LAYOUT_DICT["yaxis_title"]),
            tickvals=list(range(y_position)),
            ticktext=list(series_data.keys()),
            showticklabels=layout_settings.get("yaxis_showticklabels",DEFAULT_LAYOUT_DICT["yaxis_showticklabels"])
        ),
        xaxis=dict(
            type="date",
            tickformat="%Y-%m-%d"
        ),
        showlegend=layout_settings.get("showlegend",True),
        annotations=annotations
    )

    if(img_save):
        fig.write_image(
            out_img_settings.get("path",DEFAULT_OUT_IMG_DICT["path"]),
            width=out_img_settings.get("width",DEFAULT_OUT_IMG_DICT["width"]),
            height=out_img_settings.get("height",DEFAULT_OUT_IMG_DICT["height"]),
            scale=out_img_settings.get("scale",DEFAULT_OUT_IMG_DICT["scale"])
        )

    if(html_save):
        fig.write_html(data["out_html_path"])

    if(img_show):
        fig.show()
    return fig

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument(
        "json_path",
        type=str,
        help="JSON file path for timeline generation"
    )
    parser.add_argument(
        "--img_show",
        action="store_true",
        default=False,
        help="Whether to display the generated images"
    )
    parser.add_argument(
        "--html_save",
        action="store_true",
        default=False,
        help="Whether to convert the generated timeline to html"
    )
    args=parser.parse_args()
    
    createTimeline(args.json_path,img_show=args.img_show,html_save=args.html_save)
