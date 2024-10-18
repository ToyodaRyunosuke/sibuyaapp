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

