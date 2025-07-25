const clockContainer = document.querySelector(".js-clock"), 
dayTitle = clockContainer.querySelector("h2"),
timeTitle = clockContainer.querySelector("h3");

function getTime() {
  var date = new Date();
  var dayOptions = {year: 'numeric', month: 'long', day: 'numeric'};
  var timeOptions = {hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true};
  dayTitle.innerText = new Intl.DateTimeFormat('ko-KR', dayOptions).format(date);
  dayTitle.innerText += " 주일예배";
  timeTitle.innerText = new Intl.DateTimeFormat('ko-KR', timeOptions).format(date);
}

function init() {
  getTime();
  setInterval(getTime, 1000);
}

init();
