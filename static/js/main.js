var barColors = ["red", "green","blue","orange","brown","gray","pink","aqua","maroon","yellow"];

var currentList = document.getElementById("select-summary-list");
var defaultListId = currentList.value;
window.addEventListener('load', function() {
  handleData(defaultListId);
});

var tasksPerList = 0;
var tasksCompleted = 0;
var tasksCrossedDeadline = 0;
var tasksCompletedByDate = [];
var lastTenDates = [];

function handleData(currentListId) {
  var cards = $.get('/carddata');
  var carddata = cards.done(function (card) {
    defaultListId = currentList.value;
    tasksPerList = 0;
    tasksCompleted = 0;
    tasksCrossedDeadline = 0;
    tasksCompletedByDate = [];
    lastTenDates = [];
    
    tasksPerList = card.filter(function (c) {
      return c[1] == currentListId;
    }).length;
    
    tasksCompleted = card.filter(function (c) {
      return c[1] == currentListId && c[5] == 1;
    }).length;
    
    tasksCrossedDeadline = card.filter(function (c) {
      var deadline = new Date(c[4]);
      if (c[5] == 1) {
        var completed = new Date(c[8]);
        return c[1] == currentListId && completed > deadline;
      } else {
        var current = new Date();
        return c[1] == currentListId && current > deadline;
      }
    }).length;
    
    for (let i = 9; i >= 0; i--) {
      var current = new Date();
      current.setDate(current.getDate() - i);
      var totalCard = card.filter(function (c) {
        var completed;
        if (c[5] == 1) {
          completed = new Date(c[8]);
        }
        return c[1] == currentListId && c[5] == 1 && completed.getDate() === current.getDate();
      }).length;
      tasksCompletedByDate.push(totalCard);
      lastTenDates.push(current.getDate());
    }

    document.getElementById("tasksPerList").innerHTML = tasksPerList;
    document.getElementById("tasksCompleted").innerHTML = tasksCompleted;
    document.getElementById("tasksCrossedDeadline").innerHTML = tasksCrossedDeadline;

    new Chart("summaryChart", {
      type: "bar",
      data: {
        labels: lastTenDates,
        datasets: [{
          backgroundColor: barColors,
          data: tasksCompletedByDate
        }]
      },
      options: {
        legend: {display: false},
        title: {
          display: true,
          text: "Tasks Completed by Date"
        }
      }
    });
  });
}

currentList.addEventListener('change', function handleChange(event) {
  var currentListId = defaultListId;
  currentListId = event.target.value;
  
  handleData(currentListId);
});