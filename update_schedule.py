import urllib.request
import json
import shutil
import os
import re
from datetime import datetime

HTML_FILE = "index.html"
BACKUP_DIR = "backup"

TOURNAMENT_DATES = [
    "20260318", "20260319",
    "20260320", "20260321",
    "20260322", "20260323",
    "20260327", "20260328",
    "20260329", "20260330",
    "20260403", "20260405",
]

DATE_DISPLAY = {
    "20260318": "Wed Mar 18",
    "20260319": "Thu Mar 19",
    "20260320": "Fri Mar 20",
    "20260321": "Sat Mar 21",
    "20260322": "Sun Mar 22",
    "20260323": "Mon Mar 23",
    "20260327": "Fri Mar 27",
    "20260328": "Sat Mar 28",
    "20260329": "Sun Mar 29",
    "20260330": "Mon Mar 30",
    "20260403": "Fri Apr 3",
    "20260405": "Sun Apr 5",
}

REGION_MAP = {
    "regional 1 in fort worth": "FW1",
    "regional 2 in sacramento": "SAC2",
    "regional 3 in fort worth": "FW3",
    "regional 4 in sacramento": "SAC4",
    "final four": "F4",
    "national championship": "F4",
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<link rel="icon" href="data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20viewBox=%270%200%20110%20110%27%3E%3Ctext%20y=%271em%27%20font-size=%2790%27%3E🏀%3C/text%3E%3C/svg%3E">

<meta property="og:title" content="Simply Madness">
<meta property="og:description" content="2026 Women's March Madness viewing schedule — all games, channels, times and watch parties. Built by Carmen Daley.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://2026ncaawbbviewplan.netlify.app/">
<meta property="og:image" content="https://2026ncaawbbviewplan.netlify.app/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Simply Madness">
<meta name="twitter:image" content="https://2026ncaawbbviewplan.netlify.app/og-image.png">

<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Simply Madness</title>
<style>
  :root {
    --bg: #ffffff; --bg2: #f5f5f3; --bg3: #efefec;
    --text: #1a1a18; --text2: #5a5a56; --text3: #9a9a94;
    --border: rgba(0,0,0,0.12); --border2: rgba(0,0,0,0.22);
    --red: #E24B4A; --win: #1a6e1a; --radius: 8px;
  }
  @media (prefers-color-scheme: dark) {
    .r-FW1, .r-FW3 { color: #f09090; }
    .r-SAC2, .r-SAC4 { color: #80b8f0; }
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); font-size: 14px; padding: 16px; }
  h1 { font-size: 17px; font-weight: 600; margin-bottom: 4px; }
  .subtitle { font-size: 12px; color: var(--text3); margin-bottom: 16px; }
  .day-tabs { display: flex; gap: 5px; flex-wrap: wrap; margin-bottom: 14px; }
  .day-btn { padding: 5px 11px; border-radius: 20px; border: 1px solid var(--border2); background: transparent; color: var(--text2); cursor: pointer; font-size: 11px; line-height: 1.4; text-align: center; font-family: inherit; transition: all .15s; }
  .day-btn.active { background: var(--text); color: var(--bg); border-color: var(--text); }
  .day-btn.today { box-shadow: 0 0 0 2.5px var(--text2); }
  .day-btn.today.active { outline: 2px dotted rgba(180,180,180,0.9); outline-offset: 2px; box-shadow: none; }
  .guide-overlay{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.65);z-index:200;padding:16px;overflow-y:auto;}
  .guide-overlay.open { display:flex; }
  .guide-box { background:var(--bg); border-radius:14px; padding:20px; max-width:360px; width:100%; max-height:85vh; overflow-y:auto; }
  .guide-box h2 { font-size:15px; font-weight:800; margin-bottom:14px; color:#F47B20; }
  .guide-item { display: flex; gap: 10px; align-items: flex-start; margin-bottom: 12px; font-size: 12px; line-height: 1.4; }
  .guide-icon { font-size: 16px; flex-shrink: 0; width: 24px; text-align: center; }
  .guide-close { width: 100%; padding: 10px; margin-top: 8px; border-radius: 8px; border: none; background: #F47B20; color: white; font-size: 13px; font-weight: 600; cursor: pointer; font-family: inherit; }
  .guide-btn { padding: 5px 11px; border-radius: 20px; border: 1.5px solid #F47B20; background: transparent; color: #F47B20; cursor: pointer; font-size: 11px; font-family: inherit; font-weight: 600; margin-left: 4px; }
  .day-btn.future { opacity: 0.5; font-style: italic; }
  .sticky-day { position: sticky; top: 0; z-index: 30; background: var(--bg); padding: 6px 0 6px; display: flex; flex-direction: column; gap: 2px; border-bottom: 1px solid var(--border); margin-bottom: 12px; }
  .sticky-day-row { display: flex; align-items: center; gap: 8px; }
  .sticky-day-summary { font-size: 11px; color: var(--text2); padding: 0 2px 2px; }
  .sticky-day-pill { display: inline-flex; align-items: center; gap: 6px; background: var(--bg3); border: 1px solid var(--border2); border-radius: 20px; padding: 3px 10px; }
  .sticky-day-label { font-size: 11px; font-weight: 700; color: var(--text); }
  .sticky-round-label { font-size: 10px; color: var(--text2); }
  .guide-modal { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 100; background: rgba(0,0,0,0.5); }
  .guide-modal h2{font-size:15px;font-weight:800;color:#F47B20;margin-bottom:14px;}
  .guide-row{display:flex;gap:10px;align-items:flex-start;margin-bottom:10px;font-size:12px;line-height:1.5;}
  .guide-modal.open { display: flex; align-items: center; justify-content: center; }
  .guide-content { background: var(--bg); border-radius: 12px; padding: 20px; max-width: 360px; width: 90%; max-height: 80vh; overflow-y: auto; box-shadow: 0 8px 32px rgba(0,0,0,0.3); }
  .guide-content h2 { font-size: 15px; font-weight: 700; color: #F47B20; margin-bottom: 12px; }
  .nav-arrow { position: fixed; top: 50%; transform: translateY(-50%); z-index: 50; width: 28px; height: 56px; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.12); color: rgba(255,255,255,0.7); font-size: 20px; font-weight: 300; border-radius: 4px; cursor: pointer; user-select: none; border: none; font-family: inherit; padding: 0; }
  .nav-arrow.left { left: 0; border-radius: 0 4px 4px 0; }
  .nav-arrow.right { right: 0; border-radius: 4px 0 0 4px; }
  .nav-arrow:active { background: rgba(0,0,0,0.25); }
  .overlap-note { font-size: 11px; color: var(--text2); margin-bottom: 12px; padding: 7px 12px; background: var(--bg2); border-left: 3px solid var(--border2); border-radius: 0 var(--radius) var(--radius) 0; display: none; }
.watch-party { font-size: 11px; color: var(--text2); margin-bottom: 12px; padding: 7px 12px; background: var(--bg2); border-left: 3px solid #1a5fa0; border-radius: 0 var(--radius) var(--radius) 0; display: none; }
  .watch-party a { color: var(--text); text-decoration: none; border-bottom: 1px solid var(--border2); }
  .watch-party a:hover { color: var(--text); border-bottom-color: var(--text2); }
  .watch-party-title { font-weight: 600; margin-bottom: 5px; color: var(--text); }
  .watch-party-venues { display: flex; flex-wrap: wrap; gap: 8px; }
  .watch-party-venue { font-size: 10px; }
  .watch-party-section { margin-bottom: 5px; }
  .watch-party-section-label { font-size: 9px; font-weight: 600; text-transform: uppercase; letter-spacing: .06em; color: var(--text3); margin-bottom: 3px; }
  .future-note { font-size: 12px; color: var(--text2); padding: 24px 0; text-align: center; font-style: italic; line-height: 1.8; }
  .grid-wrap { width: 100%; }
  .grid-header { display: flex; position: sticky; top: var(--sticky-h, 42px); z-index: 19; }
  .corner { flex-shrink: 0; font-size: 10px; color: var(--text3); padding: 5px 6px; border-bottom: 1px solid var(--border); border-right: 1px solid var(--border); background: var(--bg2); display: flex; align-items: flex-end; }
  .ch-head { flex: 1; font-size: 11px; font-weight: 600; color: var(--text2); text-align: center; padding: 5px 4px; border-bottom: 1px solid var(--border); border-right: 1px solid var(--border); background: var(--bg2); white-space: nowrap; }
  .ch-head:last-child { border-right: none; }
  .grid-body { display: flex; position: relative; }
  .time-col { flex-shrink: 0; position: relative; border-right: 1px solid var(--border); }
  .time-label { position: absolute; font-size: 9px; color: var(--text3); right: 5px; white-space: nowrap; transform: translateY(-50%); }
.game-bar { position: absolute; left: 3px; right: 3px; border-radius: 5px; padding: 4px 6px; display: flex; flex-direction: column; justify-content: flex-start; overflow: hidden; background: var(--bg2); border: 1px solid var(--border2); }
  .game-bar.upset { background: #fff8e1; border: 1.5px solid #f59e0b; }
.upset-label { font-size: 9px; font-weight: 800; color: #f59e0b; letter-spacing: .06em; margin-top: 2px; }
  .cinderella-banner { font-size: 10px; color: #7c3aed; margin-bottom: 10px; padding: 7px 12px; background: #f5f3ff; border-left: 3px solid #7c3aed; border-radius: 0 var(--radius) var(--radius) 0; display: none; }
  .cinderella-label { font-size: 8px; font-weight: 700; color: #7c3aed; letter-spacing: .04em; margin-top: 1px; }
    .bar-pod { font-size: 7px; }
    .bar-team { font-size: 7.5px; }
  .bar-team.winner { color: var(--win); font-weight: 700; }
  .bar-team.loser { color: var(--text3); }
    .team-logo { width: 10px; height: 10px; }
    .bar-score-line { font-size: 7px; }
    .bar-venue { font-size: 7px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: var(--text3); margin-top: 1px; }
  .bar-link { font-size: 7px; color: var(--text3); margin-top: auto; padding-top: 2px; text-align: right; opacity: 0.65; }
  .game-bar:hover .bar-link, .game-bar:active .bar-link { opacity: 1; color: #F47B20; }
  .now-line { position: absolute; left: 0; right: 0; height: 2px; background: var(--red); opacity: 0.8; z-index: 10; pointer-events: none; }
  .now-label { position: absolute; left: 0; top: -13px; font-size: 8px; font-weight: 700; color: var(--red); white-space: nowrap; background: var(--bg); padding: 0 3px; border-radius: 3px; letter-spacing: .04em; }
  .r-FW1, .r-FW3 { color: #b03030; }
  .r-SAC2, .r-SAC4 { color: #1a5fa0; }
    .r-F4 { color: #b0a0f8; }
  @media (max-width: 500px) {
    body { padding: 8px; }
    .day-btn { font-size: 9px; padding: 3px 7px; }
  }
  .guide-modal { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 100; background: rgba(0,0,0,0.55); }</style>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap" rel="stylesheet">
</head>
<body>
<div style="display:flex;align-items:center;gap:8px;margin-bottom:2px"><span style="font-size:22px">⛹🏿‍♀️</span><h1 style="font-size:22px;font-family:'Bebas Neue',sans-serif;color:#F47B20;letter-spacing:0.04em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">2026 Women's March Madness</h1><button onclick="document.getElementById('guideOverlay').classList.add('open')" style="background:none;border:2px solid #F47B20;color:#F47B20;border-radius:50%;width:22px;height:22px;font-size:12px;font-weight:800;cursor:pointer;padding:0;line-height:1;flex-shrink:0;margin-left:8px;">?</button></div>
<p class="subtitle" id="tzSubtitle">All times Eastern · </p>
<div style="position:relative;display:flex;align-items:center;gap:4px"><button class="nav-arrow left" id="navLeft" onclick="navStep(-1)" aria-label="Previous day">&#8249;</button>
<button class="nav-arrow right" id="navRight" onclick="navStep(1)" aria-label="Next day">&#8250;</button>
<div class="day-tabs" id="dayTabs" style="flex:1;min-width:0"></div></div>
<div class="sticky-day" id="stickyDay">
<div class="sticky-day-row"><a href="https://www.espn.com/womens-college-basketball/bracket" target="_blank" style="font-size:13px;font-family:'Bebas Neue',sans-serif;letter-spacing:0.04em;color:#F47B20;margin-right:8px;white-space:nowrap;flex-shrink:0;text-decoration:none;display:inline-flex;align-items:center;"><svg width='14' height='14' viewBox='0 0 14 14' style='vertical-align:middle;margin-right:4px' xmlns='http://www.w3.org/2000/svg'><line x1='1' y1='2' x2='4' y2='2' stroke='#F47B20' stroke-width='1.5' stroke-linecap='round'/><line x1='1' y1='5' x2='4' y2='5' stroke='#F47B20' stroke-width='1.5' stroke-linecap='round'/><line x1='1' y1='9' x2='4' y2='9' stroke='#F47B20' stroke-width='1.5' stroke-linecap='round'/><line x1='1' y1='12' x2='4' y2='12' stroke='#F47B20' stroke-width='1.5' stroke-linecap='round'/><line x1='4' y1='2' x2='4' y2='5' stroke='#F47B20' stroke-width='1.5'/><line x1='4' y1='9' x2='4' y2='12' stroke='#F47B20' stroke-width='1.5'/><line x1='4' y1='3.5' x2='7' y2='3.5' stroke='#F47B20' stroke-width='1.5' stroke-linecap='round'/><line x1='4' y1='10.5' x2='7' y2='10.5' stroke='#F47B20' stroke-width='1.5' stroke-linecap='round'/><line x1='7' y1='3.5' x2='7' y2='10.5' stroke='#F47B20' stroke-width='1.5'/><line x1='7' y1='7' x2='10' y2='7' stroke='#F47B20' stroke-width='1.5' stroke-linecap='round'/><circle cx='11' cy='7' r='1.5' fill='#F47B20'/></svg>WBB Bracket</a><div class="sticky-day-pill"><span class="sticky-day-label" id="stickyDayLabel"></span><span class="sticky-round-label" id="stickyRoundLabel"></span></div><span style="margin-left:auto;font-size:10px;color:var(--text3)">Passion project by <a href="https://www.linkedin.com/in/carmendaley/" target="_blank" style="color:var(--text2);text-decoration:none;border-bottom:1px solid var(--border2);">Carmen Daley</a></span></div>
<div class="sticky-day-summary" id="daySummary"></div>
</div>
<div class="overlap-note" id="overlapNote"></div>
<div class="tbd-banner" id="tbdBanner" style="display:none;font-size:11px;color:var(--text2);margin-bottom:12px;padding:7px 12px;background:var(--bg2);border-left:3px solid #f59e0b;border-radius:0 var(--radius) var(--radius) 0;font-style:italic"></div>
<div class="cinderella-banner" id="cinderellaBanner"></div>
<div class="watch-party" id="watchParty"></div>
<div class="guide-modal" id="guideOverlay" onclick="if(event.target===this)this.classList.remove('open')">
  <div class="guide-content">
    <h2>🏀 How to use this page</h2>
    <div class="guide-item"><span class="guide-icon">📅</span><div><strong>Tabs</strong> - tap any date to see that day's games. Swipe left/right on mobile to move between days.</div></div>
    <div class="guide-item"><span class="guide-icon">📺</span><div><strong>Columns</strong> - each column is a TV channel. Games are positioned by start time so you can see overlaps.</div></div>
    <div class="guide-item"><span class="guide-icon">🏆</span><div><strong>WBB Bracket</strong> - tap the bracket link in the header to view and update your ESPN bracket.</div></div>
    <div class="guide-item"><span class="guide-icon">↗</span><div><strong>Tap any game bar</strong> - opens the ESPN game page for live scores and stats.</div></div>
    <div class="guide-item"><span class="guide-icon">🕐</span><div><strong>Timezones</strong> - times adjusted to your local timezone. Non-US timezones default to Eastern Time.</div></div>
    <div class="guide-item"><span class="guide-icon">🗓️</span><div><strong>Pods</strong> - FW1/FW3 = Fort Worth - SAC2/SAC4 = Sacramento - F4 = Phoenix</div></div>
    <div class="guide-item"><span class="guide-icon">🔴</span><div><strong>NOW line</strong> - red line shows current time on today's tab.</div></div>
    <div class="guide-item"><span class="guide-icon">🟢</span><div><strong>Green = winner</strong> - completed games show the winning team highlighted green with the final score.</div></div>
    <div class="guide-item"><span class="guide-icon">🟠</span><div><strong>Amber = upset</strong> - a lower-seeded team beat a higher seed. Look for "UNDERDOG UPSET".</div></div>
    <div class="guide-item"><span class="guide-icon">✨</span><div><strong>Cinderella</strong> - sparkle wand next to teams that reached the Sweet 16 as a #10 seed or lower.</div></div>
    <div class="guide-item"><span class="guide-icon">🫧</span><div><strong>Bubble team</strong> - blue bubbles next to teams that had to win a First Four game just to make the tournament.</div></div>
        <button class="guide-close" onclick="document.getElementById('guideOverlay').classList.remove('open')">Got it!</button>
        <p style="font-size:9px;color:var(--text3);text-align:center;margin-top:10px;">data updated %%LAST_UPDATED%% ET</p>
  </div>
</div>
<div id="gridContainer"></div>
<script>
const DURATION=120;
const PX_PER_MIN=1.0;
const TIME_COL_W=44;
const NETS=["ESPN","ABC","ESPN2","ESPNU","ESPNews"];
const G=[
%%GAME_DATA%%
];
const DAY_ORDER=["Wed Mar 18","Thu Mar 19","Fri Mar 20","Sat Mar 21","Sun Mar 22","Mon Mar 23","Fri Mar 27","Sat Mar 28","Sun Mar 29","Mon Mar 30","Fri Apr 3","Sun Apr 5"];
const days=DAY_ORDER.filter(d=>G.some(g=>g.day===d));
const roundMap={"Wed Mar 18":"First Four","Thu Mar 19":"First Four","Fri Mar 20":"Round 1","Sat Mar 21":"Round 1","Sun Mar 22":"Round 2","Mon Mar 23":"Round 2","Fri Mar 27":"Sweet 16","Sat Mar 28":"Sweet 16","Sun Mar 29":"Elite 8","Mon Mar 30":"Elite 8","Fri Apr 3":"Final Four","Sun Apr 5":"Champ."};
const futureDays=new Set(["Sun Mar 22","Mon Mar 23","Fri Mar 27","Sat Mar 28","Sun Mar 29","Mon Mar 30","Fri Apr 3","Sun Apr 5"]);
const SWEET16_DAYS=new Set(["Fri Mar 27","Sat Mar 28"]);
const ELITE8_DAYS=new Set(["Sun Mar 29","Mon Mar 30"]);
const FINAL4_DAYS=new Set(["Fri Apr 3","Sun Apr 5"]);
const deepRunDays=new Set([...SWEET16_DAYS,...ELITE8_DAYS,...FINAL4_DAYS]);

function getCinderellaTeams(){
  const cinderellas=new Set();
  G.forEach(g=>{
    if(!deepRunDays.has(g.day))return;
    const awayMatch=g.away.match(/^[(]([0-9]+)[)]/);
    const homeMatch=g.home.match(/^[(]([0-9]+)[)]/);
    if(awayMatch&&parseInt(awayMatch[1])>=10)cinderellas.add(g.away.replace(/^[(][0-9]+[)] */,""));
    if(homeMatch&&parseInt(homeMatch[1])>=10)cinderellas.add(g.home.replace(/^[(][0-9]+[)] */,""));
  });
  return cinderellas;
}
const cinderellaTeams=getCinderellaTeams();

function isCinderella(teamName){
  const bare=teamName.replace(/^[(][0-9]+[)] */,"");
  return cinderellaTeams.has(bare);
}
const now=new Date();
const todayStr=now.toLocaleDateString("en-US",{weekday:"short",month:"short",day:"numeric"}).replace(",","");
const _todayDate=new Date(now.getFullYear(),now.getMonth(),now.getDate());const todayDay=days.find(d=>d===todayStr)||days.find(d=>{const p=d.match(/(\w+) (\d+)/);if(!p)return false;const months={Jan:0,Feb:1,Mar:2,Apr:3,May:4,Jun:5,Jul:6,Aug:7,Sep:8,Oct:9,Nov:10,Dec:11};const dd=new Date(now.getFullYear(),months[p[1]],parseInt(p[2]));return dd>=_todayDate;})||days[days.length-1];
let activeDay=todayDay;
const FIRST_FOUR_DAYS=new Set(["Wed Mar 18","Thu Mar 19"]);
function getBubbleTeams(){
  const winners=new Set();
  G.forEach(g=>{
    if(!FIRST_FOUR_DAYS.has(g.day)||g.status!=="final")return;
    const ab=g.away.replace(/^[(][0-9]+[)] */,"");
    const hb=g.home.replace(/^[(][0-9]+[)] */,"");
    if(g.ascore>g.hscore)winners.add(ab);
    else if(g.hscore>g.ascore)winners.add(hb);
  });
  return winners;
}
const bubbleTeams=getBubbleTeams();
function isBubbleForDay(teamName,day){
  return bubbleTeams.has(teamName.replace(/^[(][0-9]+[)] */,""))&&!FIRST_FOUR_DAYS.has(day);
}

// toMin removed — use toLocalMin everywhere for consistency
function buildTabs(){const c=document.getElementById("dayTabs");days.forEach(d=>{const b=document.createElement("button");b.className="day-btn"+(d===activeDay?" active":"")+(futureDays.has(d)?" future":"")+(d===todayDay?" today":"");b.innerHTML=d+"<br><span style='font-size:9px;opacity:0.7'>"+(roundMap[d]||"")+"</span>";b.onclick=()=>{activeDay=d;document.querySelectorAll(".day-btn").forEach(x=>x.classList.remove("active"));b.classList.add("active");render();};c.appendChild(b);});}
  const ROUND_INFO={
    "Sun Mar 22":{total:8,partner:"Mon Mar 23",partnerShort:"the 23rd",round:"Second Round"},
    "Mon Mar 23":{total:8,partner:"Sun Mar 22",partnerShort:"the 22nd",round:"Second Round"},
    "Fri Mar 27":{total:4,partner:"Sat Mar 28",partnerShort:"the 28th",round:"Sweet 16"},
    "Sat Mar 28":{total:4,partner:"Fri Mar 27",partnerShort:"the 27th",round:"Sweet 16"},
    "Sun Mar 29":{total:2,partner:null,partnerShort:null,round:"Elite Eight"},
    "Mon Mar 30":{total:2,partner:null,partnerShort:null,round:"Elite Eight"},
    "Fri Apr 3":{total:2,partner:null,partnerShort:null,round:"Final Four",staticBlurb:"2 Final Four semifinal games at Mortgage Matchup Center in Phoenix. First tip-off at 7 PM ET on ESPN — second semifinal starts ~30 min after the first game ends."},
    "Sun Apr 5":{total:1,partner:null,partnerShort:null,round:"Championship",staticBlurb:"NCAA Championship game at Mortgage Matchup Center in Phoenix. Tip-off at 3:30 PM ET on ABC."},
  };
function render(){
  const games=G.filter(g=>g.day===activeDay);
  const realGames=games.filter(g=>g.status!=="future");
  const futureGames=games.filter(g=>g.status==="future");
  const container=document.getElementById("gridContainer");
  const note=document.getElementById("overlapNote");
  note.style.display="none";
  document.getElementById("stickyDayLabel").textContent="Viewing "+(activeDay===todayDay?(days.includes(todayStr)?"TODAY":"NEXT"):activeDay);
  document.getElementById("stickyRoundLabel").textContent=roundMap[activeDay]||"";

  const tbdBanner=document.getElementById("tbdBanner");
  const roundInfo=ROUND_INFO[activeDay];
  if(roundInfo){
    const partnerDay=roundInfo.partner;
    // Count games on THIS day without times (not pooled across partner day)
    const todayGames=G.filter(g=>g.day===activeDay);
    const todayWithTime=todayGames.filter(g=>toLocalMin(g.time)!==null).length;
    const todayTBD=todayGames.length-todayWithTime;
    // Also track partner day for context
    const partnerGames=partnerDay?G.filter(g=>g.day===partnerDay):[];
    const partnerWithTime=partnerGames.filter(g=>toLocalMin(g.time)!==null).length;
    const partnerTBD=partnerGames.length-partnerWithTime;
    const totalTBD=todayTBD+partnerTBD;
    if(roundInfo.staticBlurb){
      tbdBanner.style.display="block";
      tbdBanner.innerHTML=roundInfo.staticBlurb;
    } else if(todayTBD>0){
      tbdBanner.style.display="block";
      let blurb="";
      if(roundInfo.blurb){
        blurb=roundInfo.blurb;
      } else if(todayWithTime===0&&partnerWithTime===0){
        if(partnerDay){
          blurb=roundInfo.total+" "+roundInfo.round+" games split between "+activeDay+" and "+roundInfo.partnerShort+" - which ones air on which day is TBD!";
        } else {
          blurb=roundInfo.total+" "+roundInfo.round+(roundInfo.total===1?" game":" games")+" - matchups TBD after previous round.";
        }
      } else if(todayTBD>0){
        blurb=todayTBD+" more game"+(todayTBD===1?"":"s")+" on "+activeDay+" TBD - check back for the full slate.";
      }
      // Show known matchups with no times yet
      const _noTimeGames=G.filter(g=>{
        const onThisRound=(g.day===activeDay); // only show matchups for THIS day
        const noTime=toLocalMin(g.time)===null;
        const someTeamKnown=g.away!=="TBD"||g.home!=="TBD";
        return onThisRound&&noTime&&someTeamKnown;
      });
      if(_noTimeGames.length){
        const rows=_noTimeGames.map(g=>{
          const a=g.away==="TBD"?"TBD":(g.awayShort||g.away);
          const h=g.home==="TBD"?"TBD":(g.homeShort||g.home);
          const pod=g.reg||"";
          const pc=pod.startsWith("FW")?"#b03030":pod.startsWith("SAC")?"#1a5fa0":pod==="F4"?"#5040b0":"inherit";
          return "<div style='margin-top:3px'><span style='font-size:9px;font-weight:700;color:"+pc+";margin-right:4px'>"+pod+"</span>"+a+" vs "+h+"</div>";
        }).join("");
        blurb="<div style='margin-bottom:4px'>"+blurb+"</div>"+rows;
      }
      tbdBanner.innerHTML=blurb;
    } else {
      tbdBanner.style.display="none";
    }
  } else {
    tbdBanner.style.display="none";
  }
  
  // Day summary line
  const _summaryEl = document.getElementById('daySummary');
  if (_summaryEl) {
    const _sgames = games.filter(g => toLocalMin(g.time) !== null);
    const _allgames = games.length;
    if (_allgames === 0) {
      _summaryEl.textContent = '';
    } else if (_sgames.length === 0) {
      _summaryEl.textContent = _allgames + ' game' + (_allgames === 1 ? '' : 's') + ' - times TBD';
    } else {
      const _mins = _sgames.map(g => toLocalMin(g.time));
      const _firstMin = Math.min(..._mins);
      const _lastMin = Math.max(..._mins);
      const _endMin = _lastMin + 120;
      function _minToStr(m) {
        let h = Math.floor(m / 60) % 24;
        const mm = m % 60;
        const ap = h >= 12 ? 'PM' : 'AM';
        if (h > 12) h -= 12;
        if (h === 0) h = 12;
        return h + (mm > 0 ? ':' + String(mm).padStart(2, '0') : '') + ' ' + ap;
      }
      const _tzAbbr = _isUS ? _tzInfo.abbr : 'ET';
      const _endStr = (_endMin % 1440 === 0 || _endMin >= 1440) ? 'midnight' : _minToStr(_endMin);
      _summaryEl.textContent = _allgames + ' game' + (_allgames === 1 ? '' : 's') + ', WBB from ' + _minToStr(_firstMin) + ' til ' + (_endMin >= 1440 ? 'midnight!' : (_minToStr(_endMin) + ' ' + _tzAbbr + '!'));
    }
  }
  const scheduledGames=realGames.filter(g=>toLocalMin(g.time)!==null);
  if(!scheduledGames.length){
    const _emptyMsg=roundInfo&&roundInfo.staticBlurb?"Matchups TBD — schedule details above.":"Game times not yet announced — check back soon.";
    container.innerHTML="<div class='future-note' style='padding:20px 0'>"+_emptyMsg+"</div>";
    return;
  }
  const netsUsed=NETS.filter(n=>realGames.some(g=>g.net===n));
  const mins=realGames.map(g=>toLocalMin(g.time)).filter(Boolean);
  const dayStart=Math.floor((Math.min(...mins)-15)/30)*30;
  const dayEnd=Math.ceil((Math.max(...mins)+DURATION+15)/30)*30;
  const totalMin=dayEnd-dayStart;
  const totalPx=totalMin*PX_PER_MIN;
  // Count max simultaneous games (start each game window = start to start+DURATION)
  const scheduledTimes=realGames.map(g=>toLocalMin(g.time)).filter(n=>n!==null);
  let maxO=0;
  scheduledTimes.forEach(startMin=>{
    const simultaneous=scheduledTimes.filter(t=>t<=startMin&&t+DURATION>startMin).length;
    if(simultaneous>maxO)maxO=simultaneous;
  });
  note.style.display=maxO>=2?"block":"none";
  if(maxO>=2)note.textContent="You'd need "+maxO+" screens to watch all live D1 WBB at once!";
  const watchPartyData={
  "Wed Mar 18":[{organizer:"Marsha's 🏳️‍🌈",isAlwaysOn:true,venues:[{name:"Marsha's 🏳️‍🌈",address:"430 South St., Philadelphia",maps:"https://maps.google.com/?q=Marshas+430+South+Street+Philadelphia+PA"}]}],
  "Thu Mar 19":[{organizer:"Marsha's 🏳️‍🌈",isAlwaysOn:true,venues:[{name:"Marsha's 🏳️‍🌈",address:"430 South St., Philadelphia",maps:"https://maps.google.com/?q=Marshas+430+South+Street+Philadelphia+PA"}]}],
  "Fri Mar 20":[{organizer:"Stoop Pigeon",venues:[{name:"Yards Brewing",address:"500 Spring Garden St.",maps:"https://yardsbrewing.com/"},{name:"Dock Street South",address:"2118 Washington Ave",maps:"https://www.dockstreetbeer.com/dock-street-south-point-breeze"},{name:"Brass Tap",address:"177 Markle St.",maps:"https://www.brasstapbeerbar.com/Philadelphia"},{name:"Other Half Brewing",address:"1002 Canal St.",maps:"https://otherhalfbrewing.com/location/philadelphia/"}]},{organizer:"Marsha's 🏳️‍🌈",isAlwaysOn:true,venues:[{name:"Marsha's 🏳️‍🌈",address:"430 South St., Philadelphia",maps:"https://maps.google.com/?q=Marshas+430+South+Street+Philadelphia+PA"}]}],
  "Sat Mar 21":[{organizer:"Stoop Pigeon",venues:[{name:"Yards Brewing",address:"500 Spring Garden St.",maps:"https://yardsbrewing.com/"},{name:"Dock Street South",address:"2118 Washington Ave",maps:"https://www.dockstreetbeer.com/dock-street-south-point-breeze"},{name:"Brass Tap",address:"177 Markle St.",maps:"https://www.brasstapbeerbar.com/Philadelphia"}]},{organizer:"Marsha's 🏳️‍🌈",isAlwaysOn:true,venues:[{name:"Marsha's 🏳️‍🌈",address:"430 South St., Philadelphia",maps:"https://maps.google.com/?q=Marshas+430+South+Street+Philadelphia+PA"}]}],
  "Sun Mar 22":[{organizer:"Marsha's 🏳️‍🌈",isAlwaysOn:true,venues:[{name:"Marsha's 🏳️‍🌈",address:"430 South St., Philadelphia",maps:"https://maps.google.com/?q=Marshas+430+South+Street+Philadelphia+PA"}]}],
  "Mon Mar 23":[{organizer:"Marsha's 🏳️‍🌈",isAlwaysOn:true,venues:[{name:"Marsha's 🏳️‍🌈",address:"430 South St., Philadelphia",maps:"https://maps.google.com/?q=Marshas+430+South+Street+Philadelphia+PA"}]}],
  "Fri Mar 27":[{organizer:"Stoop Pigeon",venues:[{name:"Yards Brewing",address:"500 Spring Garden St.",maps:"https://yardsbrewing.com/"},{name:"Dock Street South",address:"2118 Washington Ave",maps:"https://www.dockstreetbeer.com/dock-street-south-point-breeze"},{name:"Brass Tap",address:"177 Markle St.",maps:"https://www.brasstapbeerbar.com/Philadelphia"}]},{organizer:"Marsha's 🏳️‍🌈",isAlwaysOn:true,venues:[{name:"Marsha's 🏳️‍🌈",address:"430 South St., Philadelphia",maps:"https://maps.google.com/?q=Marshas+430+South+Street+Philadelphia+PA"}]}],
  "Sat Mar 28":[{organizer:"Stoop Pigeon",venues:[{name:"Dock Street South",address:"2118 Washington Ave",maps:"https://www.dockstreetbeer.com/dock-street-south-point-breeze"},{name:"Brass Tap",address:"177 Markle St.",maps:"https://www.brasstapbeerbar.com/Philadelphia"}]},{organizer:"Marsha's 🏳️‍🌈",isAlwaysOn:true,venues:[{name:"Marsha's 🏳️‍🌈",address:"430 South St., Philadelphia",maps:"https://maps.google.com/?q=Marshas+430+South+Street+Philadelphia+PA"}]}],
  "Sun Mar 29":[{organizer:"Stoop Pigeon",venues:[{name:"Dock Street South",address:"2118 Washington Ave",maps:"https://www.dockstreetbeer.com/dock-street-south-point-breeze"},{name:"Brass Tap",address:"177 Markle St.",maps:"https://www.brasstapbeerbar.com/Philadelphia"}]},{organizer:"Marsha's 🏳️‍🌈",isAlwaysOn:true,venues:[{name:"Marsha's 🏳️‍🌈",address:"430 South St., Philadelphia",maps:"https://maps.google.com/?q=Marshas+430+South+Street+Philadelphia+PA"}]}],
  "Mon Mar 30":[{organizer:"Stoop Pigeon",venues:[{name:"Brass Tap",address:"177 Markle St.",maps:"https://www.brasstapbeerbar.com/Philadelphia"}]},{organizer:"Marsha's 🏳️‍🌈",isAlwaysOn:true,venues:[{name:"Marsha's 🏳️‍🌈",address:"430 South St., Philadelphia",maps:"https://maps.google.com/?q=Marshas+430+South+Street+Philadelphia+PA"}]}],
  "Fri Apr 3":[{organizer:"Stoop Pigeon",venues:[{name:"Dock Street South",address:"2118 Washington Ave",maps:"https://www.dockstreetbeer.com/dock-street-south-point-breeze"}]},{organizer:"Marsha's 🏳️‍🌈",isAlwaysOn:true,venues:[{name:"Marsha's 🏳️‍🌈",address:"430 South St., Philadelphia",maps:"https://maps.google.com/?q=Marshas+430+South+Street+Philadelphia+PA"}]}],
  "Sun Apr 5":[{organizer:"Stoop Pigeon",venues:[{name:"Two Locals Brewing",address:"3675 Market St.",maps:"https://www.twolocalsbrewing.com/"}]},{organizer:"Marsha's 🏳️‍🌈",isAlwaysOn:true,venues:[{name:"Marsha's 🏳️‍🌈",address:"430 South St., Philadelphia",maps:"https://maps.google.com/?q=Marshas+430+South+Street+Philadelphia+PA"}]}],
};
const cinderellaBanner=document.getElementById("cinderellaBanner");
  const daycinderellas=[...cinderellaTeams].filter(t=>
    realGames.some(g=>g.away.includes(t)||g.home.includes(t))
  );
  if(daycinderellas.length){
    cinderellaBanner.style.display="block";
    const names=daycinderellas.length===1?daycinderellas[0]:daycinderellas.slice(0,-1).join(", ")+" & "+daycinderellas[daycinderellas.length-1];
    cinderellaBanner.innerHTML="<b>\u2728 Cinderella alert</b> \u2014 "+names+(daycinderellas.length===1?" is":" are")+" still dancing!";
  } else {
    cinderellaBanner.style.display="none";
  }

  const watchParty=document.getElementById("watchParty");
  const groups=watchPartyData[activeDay];
  const alwaysOn=groups?groups.filter(g=>g.isAlwaysOn):[];
  const eventGroups=groups?groups.filter(g=>!g.isAlwaysOn):[];
  if(alwaysOn.length||eventGroups.length){
    watchParty.style.display="block";
    let wp="<div class='watch-party-title'>Watch Women's Madness in Philly</div>";
    alwaysOn.forEach(g=>{
      g.venues.forEach(v=>{
        wp+="<div style='margin:3px 0'><a href='"+v.maps+"' target='_blank' style='font-size:11px;font-weight:700;color:var(--text);text-decoration:none;border-bottom:1px solid var(--border2)'>"+v.name+"</a>";
        wp+=" <span style='font-size:9px;color:var(--text3)'>"+v.address+" &mdash; always showing women's sports</span></div>";
      });
    });
    if(eventGroups.length){
      wp+="<div style='font-size:9px;font-weight:600;color:var(--text3);text-transform:uppercase;letter-spacing:.05em;margin-top:6px;margin-bottom:3px'>Stoop Pigeon watch parties</div>";
      wp+="<div class='watch-party-venues'>";
      eventGroups.forEach(g=>{
        g.venues.forEach(v=>{
          wp+="<div class='watch-party-venue'><a href='"+v.maps+"' target='_blank'>"+v.name+"</a> <span style='color:var(--text3)'>"+v.address+"</span></div>";
        });
      });
      wp+="</div>";
    }
    watchParty.innerHTML=wp;
  } else {
    watchParty.style.display="none";
  }
  const ticks=[];
  for(let t=dayStart;t<=dayEnd;t+=30)ticks.push(t);
  const now=new Date();
  const isToday=activeDay===todayStr;
  const nowMin=now.getHours()*60+now.getMinutes();
  const showNow=isToday&&nowMin>=dayStart&&nowMin<=dayEnd;
  const nowPct=showNow?((nowMin-dayStart)/totalMin*100):null;
  let html="<div class='grid-wrap'>";
  html+="<div class='grid-header'>";
  html+="<div class='corner' style='width:"+TIME_COL_W+"px;min-width:"+TIME_COL_W+"px'>"+_tzLabel+"</div>";
  netsUsed.forEach(n=>{html+="<div class='ch-head'>"+n+"</div>";});
  html+="</div><div class='grid-body'>";
  html+="<div class='time-col' style='width:"+TIME_COL_W+"px;min-width:"+TIME_COL_W+"px;height:"+totalPx+"px;position:relative'>";
  ticks.forEach(t=>{
    const yPct=(t-dayStart)/totalMin*100;
    const h24=Math.floor(t/60),m=t%60,ap=h24>=12?"PM":"AM",h12=h24>12?h24-12:(h24===0?12:h24);
    const lbl=m===0?(h12+" "+ap):(h12+":"+String(m).padStart(2,"0"));
    html+="<div class='time-label' style='top:"+yPct+"%'>"+lbl+"</div>";
    html+="<div style='position:absolute;right:0;left:0;top:"+yPct+"%;height:1px;background:var(--border)'></div>";
  });
  if(nowPct!==null)html+="<div style='position:absolute;right:0;left:0;top:"+nowPct+"%;height:2px;background:var(--red);opacity:0.8'></div>";
  html+="</div>";
  html+="<div style='display:flex;flex:1;height:"+totalPx+"px;position:relative'>";
  ticks.forEach(t=>{
    const yPct=(t-dayStart)/totalMin*100;
    html+="<div style='position:absolute;left:0;right:0;top:"+yPct+"%;height:1px;background:var(--border);opacity:"+(t%60===0?0.5:0.2)+";z-index:0'></div>";
  });
  if(nowPct!==null)html+="<div class='now-line' style='top:"+nowPct+"%'><span class='now-label'>NOW</span></div>";
  netsUsed.forEach((net,ni)=>{
    const netGames=realGames.filter(g=>g.net===net);
    const leftPct=ni/netsUsed.length*100;
    const widthPct=1/netsUsed.length*100;
    html+="<div style='position:absolute;left:"+leftPct+"%;width:"+widthPct+"%;top:0;bottom:0;"+(ni<netsUsed.length-1?"border-right:1px solid var(--border)":"")+"'>";
    netGames.forEach(g=>{
      const s=toLocalMin(g.time);
      const espnUrl=g.gameId?"https://www.espn.com/womens-college-basketball/game/_/gameId/"+g.gameId:"";
      if(!s)return;
      const yPct=(s-dayStart)/totalMin*100;
      const hPct=DURATION/totalMin*100;
      const rc="r-"+g.reg;
      const isFinal=g.status==="final";
      const awayWon=isFinal&&g.ascore!=null&&g.ascore>g.hscore;
      const homeWon=isFinal&&g.hscore!=null&&g.hscore>g.ascore;
      const awayCls=isFinal?(awayWon?"winner":"loser"):"";
      const homeCls=isFinal?(homeWon?"winner":"loser"):"";
      const awayLogoHtml=g.awayLogo?"<img src='"+g.awayLogo+"' class='team-logo'>":"";
      const homeLogoHtml=g.homeLogo?"<img src='"+g.homeLogo+"' class='team-logo'>":"";
      const wandSVG="<svg width='10' height='10' viewBox='0 0 10 10' style='margin-left:2px;flex-shrink:0'><line x1='5' y1='0' x2='5' y2='3' stroke='#7c3aed' stroke-width='1.2' stroke-linecap='round'/><line x1='5' y1='7' x2='5' y2='10' stroke='#7c3aed' stroke-width='1.2' stroke-linecap='round'/><line x1='0' y1='5' x2='3' y2='5' stroke='#7c3aed' stroke-width='1.2' stroke-linecap='round'/><line x1='7' y1='5' x2='10' y2='5' stroke='#7c3aed' stroke-width='1.2' stroke-linecap='round'/><line x1='1.5' y1='1.5' x2='3.5' y2='3.5' stroke='#7c3aed' stroke-width='1' stroke-linecap='round'/><line x1='6.5' y1='6.5' x2='8.5' y2='8.5' stroke='#7c3aed' stroke-width='1' stroke-linecap='round'/><line x1='8.5' y1='1.5' x2='6.5' y2='3.5' stroke='#7c3aed' stroke-width='1' stroke-linecap='round'/><line x1='1.5' y1='8.5' x2='3.5' y2='6.5' stroke='#7c3aed' stroke-width='1' stroke-linecap='round'/><circle cx='5' cy='5' r='1.5' fill='#7c3aed'/></svg>";
      const awayWandHtml=isCinderella(g.away)?wandSVG:"";
      const bubbleSVG="<svg width='20' height='18' viewBox='0 0 20 18' style='margin-left:3px;flex-shrink:0;vertical-align:middle'><circle cx='7.5' cy='10' r='6' fill='rgba(56,189,248,0.15)' stroke='rgba(56,189,248,0.7)' stroke-width='1.1'/><circle cx='5.5' cy='8' r='1.8' fill='white' opacity='0.55'/><circle cx='8.5' cy='7' r='0.7' fill='white' opacity='0.45'/><circle cx='14.5' cy='7.5' r='3.5' fill='rgba(56,189,248,0.12)' stroke='rgba(56,189,248,0.6)' stroke-width='0.9'/><circle cx='13.2' cy='6' r='1' fill='white' opacity='0.55'/><circle cx='15' cy='13.5' r='2.2' fill='rgba(56,189,248,0.1)' stroke='rgba(56,189,248,0.55)' stroke-width='0.8'/><circle cx='14' cy='12.5' r='0.6' fill='white' opacity='0.5'/></svg>";
      const awayBubbleHtml=isBubbleForDay(g.away,g.day)?bubbleSVG:"";
      const homeBubbleHtml=isBubbleForDay(g.home,g.day)?bubbleSVG:"";
      const homeWandHtml=isCinderella(g.home)?wandSVG:"";
      const awaySeeds=g.away.match(/^[(]([0-9]+)[)]/);
      const homeSeeds=g.home.match(/^[(]([0-9]+)[)]/);
      const awaySeed=awaySeeds?parseInt(awaySeeds[1]):null;
      const homeSeed=homeSeeds?parseInt(homeSeeds[1]):null;
      const isUpset=isFinal&&awaySeed&&homeSeed&&((awayWon&&awaySeed>homeSeed)||(homeWon&&homeSeed>awaySeed));
      const cinLabel=(isCinderella(g.away)||isCinderella(g.home))?"<span style='font-size:8px;font-weight:800;color:#7c3aed;margin-left:6px;letter-spacing:.04em'>CINDERELLA</span>":"";
      if(espnUrl)html+="<a href='"+espnUrl+"' target='_blank' style='text-decoration:none;color:inherit;display:contents'>";
      html+="<div class='game-bar"+(isUpset?" upset":"")+"' style='top:"+yPct+"%;height:"+hPct+"%'><div style='position:absolute;top:3px;right:4px;font-size:7px;color:var(--text3);opacity:0.7;pointer-events:none'>open game page ↗</div>";
      html+="<div class='bar-pod "+rc+"' style='display:flex;align-items:center'>"+g.reg+cinLabel+"</div>";
      html+="<div class='bar-team "+awayCls+"'>"+(awayLogoHtml)+(window.innerWidth<500?(g.awayAbbr||g.awayShort||g.away):g.away)+awayWandHtml+awayBubbleHtml+"</div>";
      html+="<div class='bar-team "+homeCls+"'>"+(homeLogoHtml)+(window.innerWidth<500?(g.homeAbbr||g.homeShort||g.home):g.home)+homeWandHtml+homeBubbleHtml+"</div>";
      if(isFinal&&g.ascore!=null)html+="<div class='bar-score-line'>"+g.ascore+" \u2013 "+g.hscore+"</div>";
      if(isUpset)html+="<div class='upset-label'>UNDERDOG UPSET</div>";
      if(g.time&&g.time!=='TBD'&&g.time!=='12:00 AM'){
        const lt=toLocalTime(g.time);
        if(lt){const _tDisp=lt.replace(':00','');html+="<div style='font-size:7px;color:var(--text3);margin-top:1px'>"+_tDisp+" "+(_isUS?_tzInfo.abbr:'ET')+" start</div>";}
      }
      if(g.venue){
        const vparts=g.venue.split(', ');
        const vCity=vparts.slice(1).join(', ');
        html+="<div class='bar-venue'>"+(vCity||g.venue)+"</div>";
      }
      if(espnUrl)html+="<div class='bar-link'>Open game page &#8599;</div>";
      html+="</div>";
      if(espnUrl)html+="</a>";
    });
    html+="</div>";
  });
  html+="</div></div></div>";
  container.innerHTML=html;
}

  let _tx=0,_ty=0;
  document.addEventListener('touchstart',e=>{_tx=e.touches[0].clientX;_ty=e.touches[0].clientY;},{passive:true});
  document.addEventListener('touchend',e=>{
    const dx=e.changedTouches[0].clientX-_tx,dy=e.changedTouches[0].clientY-_ty;
    if(Math.abs(dx)<50||Math.abs(dx)<Math.abs(dy)*1.5)return;
    const idx=days.indexOf(activeDay),ni=dx<0?idx+1:idx-1;
    if(ni<0||ni>=days.length)return;
    activeDay=days[ni];
    document.querySelectorAll('.day-btn').forEach((b,i)=>{
      b.classList.remove('active');
      if(days[i]===activeDay){b.classList.add('active');b.style.transition='none';b.style.boxShadow='0 0 0 3px #F47B20';setTimeout(()=>{b.style.boxShadow='';b.style.transition='';},300);b.scrollIntoView({behavior:'smooth',block:'nearest',inline:'center'});}
    });
    render();
    },{passive:true});

  let _ha=null;
  document.addEventListener('visibilitychange',()=>{if(document.hidden){_ha=Date.now();}else{if(_ha&&Date.now()-_ha>15*60*1000){location.reload();}_ha=null;}});

  if('ontouchstart' in window){}

  function updateStickyHeight(){
    const sd=document.getElementById('stickyDay');
    if(sd)document.documentElement.style.setProperty('--sticky-h',sd.offsetHeight+'px');
  }
  updateStickyHeight();
  window.addEventListener('resize',updateStickyHeight);

  // Timezone detection and conversion
  const _userTZ = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const US_TZ_MAP = {
    'America/New_York':             { name: 'Eastern Time',  abbr: 'ET',  etDiff: 0 },
    'America/Detroit':              { name: 'Eastern Time',  abbr: 'ET',  etDiff: 0 },
    'America/Indiana/Indianapolis': { name: 'Eastern Time',  abbr: 'ET',  etDiff: 0 },
    'America/Kentucky/Louisville':  { name: 'Eastern Time',  abbr: 'ET',  etDiff: 0 },
    'America/Chicago':              { name: 'Central Time',  abbr: 'CT',  etDiff: -1 },
    'America/Indiana/Knox':         { name: 'Central Time',  abbr: 'CT',  etDiff: -1 },
    'America/Menominee':            { name: 'Central Time',  abbr: 'CT',  etDiff: -1 },
    'America/Denver':               { name: 'Mountain Time', abbr: 'MT',  etDiff: -2 },
    'America/Boise':                { name: 'Mountain Time', abbr: 'MT',  etDiff: -2 },
    'America/Phoenix':              { name: 'Mountain Time', abbr: 'MT',  etDiff: -2 },
    'America/Los_Angeles':          { name: 'Pacific Time',  abbr: 'PT',  etDiff: -3 },
    'America/Anchorage':            { name: 'Alaska Time',   abbr: 'AKT', etDiff: -4 },
    'America/Juneau':               { name: 'Alaska Time',   abbr: 'AKT', etDiff: -4 },
    'Pacific/Honolulu':             { name: 'Hawaii Time',   abbr: 'HT',  etDiff: -6 },
  };
  const _tzInfo = US_TZ_MAP[_userTZ] || null;
  const _isET = _tzInfo ? _tzInfo.abbr === 'ET' : false;
  const _isUS = !!_tzInfo;
  const _tzLabel = _tzInfo ? _tzInfo.name : 'Eastern Time';

  function toLocalTime(etStr) {
    if (!etStr || etStr === 'TBD' || etStr === '12:00 AM') return etStr;
    if (!_isUS || _isET) return etStr;
    const [hm, ap] = etStr.split(' ');
    let [h, m] = hm.split(':').map(Number);
    if (ap === 'PM' && h !== 12) h += 12;
    if (ap === 'AM' && h === 12) h = 0;
    let lh = h + _tzInfo.etDiff;
    if (lh < 0) lh += 24;
    if (lh >= 24) lh -= 24;
    const lap = lh >= 12 ? 'PM' : 'AM';
    let h12 = lh > 12 ? lh - 12 : (lh === 0 ? 12 : lh);
    return h12 + (m > 0 ? ':' + String(m).padStart(2, '0') : '') + ' ' + lap;
  }

  function toLocalMin(etStr) {
    if (!etStr || etStr === 'TBD' || etStr === '12:00 AM') return null;
    const local = toLocalTime(etStr);
    if (!local || local === 'TBD' || local === '12:00 AM') return null;
    const [hm, ap] = local.split(' ');
    const parts = hm.split(':');
    let h = Number(parts[0]), m = parts.length > 1 ? Number(parts[1]) : 0;
    if (ap === 'PM' && h !== 12) h += 12;
    if (ap === 'AM' && h === 12) h = 0;
    return h * 60 + m;
  }

  // Update subtitle
  const _tzSubEl = document.getElementById('tzSubtitle');
  if (_tzSubEl) {
    if (!_isUS) {
      _tzSubEl.textContent = 'Times in Eastern Time - your timezone is not supported, defaulting to ET - Tap a day to navigate';
    } else if (_isET) {
      _tzSubEl.textContent = 'All times Eastern - Tap a day to navigate';
    } else {
      _tzSubEl.textContent = 'Times in your local timezone (' + _tzInfo.name + ') - Tap a day to navigate';
    }
  }

  function navStep(dir){
    const idx=days.indexOf(activeDay);
    const ni=idx+dir;
    if(ni<0||ni>=days.length)return;
    activeDay=days[ni];
    document.querySelectorAll(".day-btn").forEach((b,i)=>{
      b.classList.remove("active");
      if(days[i]===activeDay){
        b.classList.add("active");
        b.scrollIntoView({behavior:"smooth",block:"nearest",inline:"center"});
      }
    });
    updateNavArrows();
    render();
  }
  function updateNavArrows(){
    const idx=days.indexOf(activeDay);
    const l=document.getElementById("navLeft");
    const r=document.getElementById("navRight");
    if(l)l.style.display=idx===0?"none":"flex";
    if(r)r.style.display=idx===days.length-1?"none":"flex";
  }
buildTabs();render();updateStickyHeight();updateNavArrows();
</script>
</body>
</html>"""

def backup_html():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(BACKUP_DIR, f"wbb_schedule_{timestamp}.html")
    shutil.copy2(HTML_FILE, path)
    print(f"  Backup saved: {path}")

def fetch_games_for_date(date_str):
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/womens-college-basketball/scoreboard?dates={date_str}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())
            return data.get("events", [])
    except Exception as e:
        print(f"  Error fetching {date_str}: {e}")
        return []

def detect_region_from_headline(event):
    try:
        notes = event["competitions"][0].get("notes", [])
        for note in notes:
            headline = note.get("headline", "").lower()
            for key, reg in REGION_MAP.items():
                if key in headline:
                    return reg
    except:
        pass
    return None

def get_network(event):
    try:
        broadcasts = event["competitions"][0].get("broadcasts", [])
        if broadcasts:
            names = broadcasts[0].get("names", [])
            if names:
                return names[0]
    except:
        pass
    return "ESPN"

def get_teams(event):
    try:
        competitors = event["competitions"][0]["competitors"]
        home = next(c for c in competitors if c["homeAway"] == "home")
        away = next(c for c in competitors if c["homeAway"] == "away")
        return (
            away["team"]["displayName"],
            home["team"]["displayName"],
            away.get("curatedRank", {}).get("current", ""),
            home.get("curatedRank", {}).get("current", ""),
            away["team"].get("logo", ""),
            home["team"].get("logo", ""),
            away["team"].get("shortDisplayName", away["team"]["displayName"]),
            home["team"].get("shortDisplayName", home["team"]["displayName"]),
            away["team"].get("abbreviation", ""),
            home["team"].get("abbreviation", ""),
        )
    except:
        return "TBD", "TBD", "", "", "", "", "TBD", "TBD", "", ""

def get_venue(event):
    try:
        venue = event["competitions"][0]["venue"]
        city = venue["address"]["city"]
        state = venue["address"]["state"]
        name = venue.get("fullName", "")
        return f"{name}, {city}, {state}" if name else f"{city}, {state}"
    except:
        return "TBD"

def get_time(event):
    try:
        detail = event["status"]["type"]["detail"]
        match = re.search(r'at\s+([\d:]+\s*[AP]M)', detail)
        if match:
            return match.group(1).strip()
        date_str = event.get("date", "")
        if date_str:
            from datetime import timezone, timedelta
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%MZ")
            dt_et = dt - timedelta(hours=4)
            hour = dt_et.hour
            minute = dt_et.minute
            ap = "PM" if hour >= 12 else "AM"
            h12 = hour - 12 if hour > 12 else (12 if hour == 0 else hour)
            return f"{h12}:{str(minute).zfill(2)} {ap}"
    except:
        pass
    return "TBD"

def get_status(event):
    try:
        status_obj = event["competitions"][0].get("status", event.get("status", {}))
        completed = status_obj["type"]["completed"]
        state = status_obj["type"]["state"]
        if completed:
            return "final"
        if state == "in":
            return "live"
    except:
        pass
    return "upcoming"

def get_scores(event):
    try:
        competitors = event["competitions"][0]["competitors"]
        home = next(c for c in competitors if c["homeAway"] == "home")
        away = next(c for c in competitors if c["homeAway"] == "away")
        ascore = int(float(away.get("score", 0)))
        hscore = int(float(home.get("score", 0)))
        if ascore == 0 and hscore == 0:
            return None, None
        return ascore, hscore
    except:
        return None, None

def get_game_id(event):
    try:
        return event.get("id", "")
    except:
        return ""

def format_team(name, seed):
    if seed and str(seed) not in ("", "99"):
        return f"({seed}) {name}"
    return name

def build_entry(day, time, net, away, home, reg, venue, status, ascore, hscore, away_logo, home_logo, away_short="", home_short="", away_abbr="", home_abbr="", game_id=""):
    away = away.replace('"', '\\"')
    home = home.replace('"', '\\"')
    venue = venue.replace('"', '\\"')
    away_logo = away_logo.replace('"', '\\"')
    home_logo = home_logo.replace('"', '\\"')
    away_short = away_short.replace('"', '\\"')
    home_short = home_short.replace('"', '\\"')
    game_id = str(game_id)
    away_abbr = away_abbr.replace('"', '\\"')
    home_abbr = home_abbr.replace('"', '\\"')
    entry = f'  {{day:"{day}",time:"{time}",net:"{net}",away:"{away}",home:"{home}",awayShort:"{away_short}",homeShort:"{home_short}",awayAbbr:"{away_abbr}",homeAbbr:"{home_abbr}",gameId:"{game_id}",reg:"{reg}",venue:"{venue}",awayLogo:"{away_logo}",homeLogo:"{home_logo}"'
    if status == "final" and ascore is not None and hscore is not None:
        entry += f',ascore:{ascore},hscore:{hscore},status:"final"'
    elif status == "live":
        entry += ',status:"live"'
    entry += '},\n'
    return entry

def fetch_all_games():
    all_entries = []
    total = 0
    all_events_by_date = {}
    for date_str in TOURNAMENT_DATES:
        events = fetch_games_for_date(date_str)
        tourney = [
            e for e in events
            if e.get("competitions", [{}])[0].get("type", {}).get("abbreviation") == "TRNMNT"
        ]
        all_events_by_date[date_str] = tourney

    team_to_pod = {}
    for date_str, events in all_events_by_date.items():
        for event in events:
            reg = detect_region_from_headline(event)
            if reg and reg != "F4":
                away_full, home_full, _, _, _, _, _, _, _, _ = get_teams(event)
                if away_full != "TBD":
                    team_to_pod[away_full] = reg
                if home_full != "TBD":
                    team_to_pod[home_full] = reg

    print(f"  Built pod lookup for {len(team_to_pod)} teams")

    for date_str in TOURNAMENT_DATES:
        day_label = DATE_DISPLAY[date_str]
        events = all_events_by_date.get(date_str, [])
        if not events:
            continue
        print(f"  {day_label}: {len(events)} game(s)")
        total += len(events)
        for event in events:
            away_full, home_full, away_seed, home_seed, away_logo, home_logo, away_short_name, home_short_name, away_abbr_raw, home_abbr_raw = get_teams(event)
            away = format_team(away_full, away_seed)
            home = format_team(home_full, home_seed)
            time   = get_time(event)
            net    = get_network(event)
            venue  = get_venue(event)
            status = get_status(event)
            ascore, hscore = get_scores(event) if status == "final" else (None, None)
            reg = detect_region_from_headline(event)
            if reg is None:
                reg = team_to_pod.get(away_full) or team_to_pod.get(home_full)
            if reg is None:
                reg = "FW1"
                print(f"  WARNING: Could not detect pod for {away_full} vs {home_full}")
            away_short = format_team(away_short_name, away_seed)
            home_short = format_team(home_short_name, home_seed)
            away_abbr_fmt = format_team(away_abbr_raw, away_seed)
            home_abbr_fmt = format_team(home_abbr_raw, home_seed)
            game_id = get_game_id(event)
            entry = build_entry(day_label, time, net, away, home,
                                reg, venue, status, ascore, hscore, away_logo, home_logo,
                                away_short, home_short, away_abbr_fmt, home_abbr_fmt, game_id)
            all_entries.append(entry)

    print(f"\n  Total games fetched: {total}")
    return all_entries

def main():
    print("\n" + "="*60)
    print("  WBB Schedule — Full Rebuild from ESPN API")
    print(f"  {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print("="*60)

    print("\n[1] Backing up current file...")
    backup_html()

    print("\n[2] Fetching all tournament games from ESPN...")
    entries = fetch_all_games()

    print("\n[3] Building fresh HTML file...")
    game_data = "".join(entries)
    from datetime import timezone, timedelta
    et_now = datetime.now(timezone.utc) - timedelta(hours=4)
    ts = et_now.strftime("%b %d, %I:%M %p").lstrip("0")
    html = HTML_TEMPLATE.replace("%%GAME_DATA%%", game_data)
    html = html.replace("%%LAST_UPDATED%%", ts)
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print("  Done.")

    print("\n[4] Verifying...")
    with open(HTML_FILE, encoding="utf-8") as f:
        content = f.read()
    count = len(re.findall(r'day:"', content))
    import collections
    regs = re.findall(r'reg:"(\w+)"', content)
    finals = len(re.findall(r'status:"final"', content))
    print(f"  Total entries : {count}")
    print(f"  Finals w/scores: {finals}")
    print(f"  Pod breakdown : {dict(collections.Counter(regs))}")

    print(f"\n  --> Upload {HTML_FILE} to Netlify to update your page.")
    print("\n" + "="*60)
    print("  Finished!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
