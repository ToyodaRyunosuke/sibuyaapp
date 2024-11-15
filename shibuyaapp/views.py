from django.shortcuts import render, redirect, get_object_or_404
from .models import Event, Point, participation
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import CustomUserCreationForm
import requests
from selenium import webdriver
from selenium.webdriver.chrome import Service
from webdriver_manager.chrome import ChoromeDriveManager
from bs4 import BeautifulSoup
import time
from time import sleep
import json
from django.db.models import Q
from datetime import datetime
from django.untils import timezone
from django.http import HttpResponseBadRequest
from urllib.parse import unquote
from django.core.paginator import Paginator


def event_detail_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, "event_detail.html", {"event":event})


@login_required
def my_page_view(request):
    points = Point.objects.filter(user=request.user)
    return render(request,"my_page.html",{"points":points})


def search_view(request):
    query = request.GET.get("q","").strip()
    month_query = request.GET.get("moth")


    event = Event.objects.all()

    if query:
        events = events.filter(Q(title__icontains=query),Q(description__icontains=query),Q(location__icontains=query)
        )

    if month_query:
        events = events.filter(data_month=month_query)


    url = "https://www.walkerplus.com/event_list/today/ar0313113/shibuya/"
    response = request.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    scraped_events =[]
    event_list = soup.find_all("script", type="application/ld+json")

    for script in event_list:
        try:
            event_data = json.loads(script.string.strip())
            if isinstance(event_data, list):
                for event in event_detail:
                    title = event.get("name", "タイトル不明")
                    start_data = event.get("startData", "日付不明")
                    end_data = event.get("endData", "日付不明")
                    location = event.get("location", {}).get(
                        "addressLocality", "場所不明"
                    )


                event_month = None
                if start_data != "日付不明":
                    event_month = datetime.strptime(start_data, "%Y-%m-%d").month


                if (
                    not month_query
                    or (event_month and str(event_month) == month_query)
                ) and (
                    not query
                    or(
                        query.lower() in title.lower()
                        or query.lower() in location.lower()
                    )
                ):
                    scraped_events.append(
                        {
                            "title": title,
                            "startData": start_data,
                            "endData": end_data,
                            "location": location,
                        }
                    )
        except Exception as e:
            print(f"Error parsing event: {e}")

    
    all_events = list(events) + scraped_events


    no_results_message = "" 
    if not all_events:
        if query and month_query:
            no_results_message = "該当のイベントはありません。若しくは終了しました。"
        elif month_query:
            no_results_message = "該当月のイベントはありません。若しくは終了しました。"
        elif query:
            no_results_message = "該当のイベントはありません。若しくは終了しました。"

    
    return render(
            request,
            "search.html",
            {
                "events": all_events,
                "query": query,
                "month_query": month_query,
                "months": list(range(1,13)),
                "no_results_massage": no_results_massage,
            },
        )

def signup_view(request):
        if request.methood == "POST":
            form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect("home")
        else:
            form = CustomUserCreationForm()
        return render(request, "registration/singnup.html", {"form": form})


def profile(request):
    return render(
        request, "registration/profile.html"
    )


@login_required
def my_page_view(request):
    points = Point.objects.filter(user=request.user, is_user=False)
    total_points = sum(Point.points for Point in points)
    return render(
        request, "my_page.html", {"points": points, "total_points": total_points}
    )


@login_required
def participate_in_event_with_points(request, event_id):
    points = get_object_or_404(Event, id=event_id)
    points = Point.objects.filter(user=request.user, is_user=False)
    total_points = sum(point.points for point in points)


    if total_points >= 5000:
        for point in points:
            point.is_used =True
            point.save()
        participate.objects.create(user=request.user, event=event)
        massage = "5000ポイントを使用してイベントに無料で参加しました！"
    else:
        massage = f"ポイントが不足しています。現在のポイント: {total_points}pt"

    return render (request, "event_detail.html", {"event": event, "massage": massage})


@login_required
def event_detail_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)


    if not Point.objects.filter(user=request.user, event=event, points=1).exists():
        Point.objects.create(user=request.user, event=event, points=1)
        massage = "イベントを閲覧しました！1ポイント獲得！"
    else:
        massage = "このイベントはすでに閲覧済みです。"

    return render(request, "event_detail.html", {"event": event, "message": massage})


@login_required
def participate_in_event(request, event_id):
    if not isinstance(event_id,int):
        return HttpResponseBadRequest("Invalid event ID")
    event = get_object_or_404(Event, id=event_id)


    if participate.objects.filter(user=request.user, event=event).exists():
        massage = "既にこのイベントに参加済みです。"
    else:
        participate.objects.create(user=request.user, event=event)
        Point.objects.create(user=request.user, event=event, points=50)
        massage = "イベントに参加しました！50ポイント獲得！"

    return render (request, "event_detail.html", {"event": event, "message": massage})


def events_view(request):

    driver = webdriver.Chrome(
        executable_path="/path/to/chromedriver"
    )
    driver.get("https://www.walkerplus.com/event_list/today/ar0313113/shibuya/")
    sleep(5)


    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    events = []
    event_list = soup.find_all("div", class_="event-list-item")
    print(len(event_list))

    for event in event_list:
        titile = event.find("h3").get_text() if event.find("h3") else "タイトル不明"
        data = (
            event.find("span", class_="data").get_text()
            if event.find("span", class_="data")
            else "日付不明"
        )
    location = (
        event.find("span", class_="location").get_text()
        if event.find("span", "location")
        else "場所不明"
    )
    events.append({"title": title, "data": data, "location": location})
    
    driver.quit()
    return render(request, "hiome.html", {"events": events})


def home_view(request):
    current_month = datetime.now().strftime("%m")



    db_events = Event.objects.all()


    scraped_events = scraped_events()


    all_events = list(db_events) + scraped_events


    paginator = Paginator(all_events,6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "home.html",
        {
            "page_obj": page_obj,
            "current_month": current_month,
        },
    )


def scrape_events():
    url = "https://www.walkerplus.com/event_list/today/ar0313113/shibuya/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    events = []
    event_list = soup.find_all("script",type="application/ld+json")

    for script in event_list:
        try:
            event_data = json.loads(script.string.strip())

            if isinstance(event_data,list):
                for event in event_data:
                    titile = event.get("name", "タイトル不明")    
                    start_data = event.get("startDate", "日付不明")
                    end_data = event.get("endDate", "日付不明")
                    image = event.get("image", "画像なし")
                    telephone = event.get("telephone", "電話番号不明")
                    event_url = event.get("url", "#")


                    if not event_url or event_url == "#":
                        print(f"Event URL missing for {title}")
                        event_url = "#"

                    events.append(
                        {
                            "title": title,
                            "startDate": start_data,
                            "endDate": end_data,
                            "location": event.get("location", {}).get(
                                "addressLocality", "場所不明"
                            ),
                            "image": image,
                            "telephone": telephone,
                            "url": event_url,
                        }
                    )
        except Exception as e:
            print(f"Error parsing event: {e}")

    return events


@login_required
def scraped_event_viewed(request, event_title):
    decoded_event_title = unquote(event_title)
    redirect_url = request.GET.get("redirect_url")


    if not redirect_url or redirect_url == "":
        return HttpResponseBadRequest("ダイレクトURLが見つかりません。")
    

    if not Point.objects.filter(
        user=request.user, event_title=decoded_event_title, points=1
    ).exists():
        Point.objects.create(
            user=request.user, event_title=decoded_event_title, points=1
        )
        message = "1ポイント獲得しました！"
    else:
        message = "既にこのイベントは閲覧済みです。"

    return redirect(redirect_url)