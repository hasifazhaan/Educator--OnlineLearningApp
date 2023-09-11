$(document).ready(()=>{
  
  $.ajax({
    type: "POST",
    url: "/timeslogin",
    success: function(result) {
      chart1(result['data'])
    } 
  });

// $.ajax({
//     type:"GET",
//     url:"/usercourse",
//     success: function(result){
//       alert("Made")
//     }
//   });
// let container = $('#overview')
// let colno = 0
// coursename = "Abc"


// let row  =
// `<div class="row"></div>`

// let colums = `
// <div class = 'col'>
//   <div class="chart" >
//     <h5>${coursename}</h5>
//     <canvas id="${colno}"></canvas>
//   </div>
// </div> `

// container.append(colums)

});


const chart1 = (data1)=>{
  const labels = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
  ];
  const data = {
    labels: labels,
    datasets: [{
      label: 'User Access Time  ',
      backgroundColor: 'rgb(255, 99, 150)',
      borderColor: 'rgb(222, 4, 50)',
      data: data1,
    }]
  };
  const config = {
    type: 'line',
    data: data,
    options: {}
  };

  const myChart1 = new Chart(
    document.getElementById('userlogin'),
    config
);

$.ajax({
  type:"POST",
  url:"/usercourse",
  success: function(result){
    chart2(result['data'])
  }
});

}

function getRandomColor(no) {
  listval = Array()
  var letters = '0123456789ABCDEF';
  var color = '#';
  for (var i = 0 ; i < no ;i++){


    for (var j = 0; j < 6; j++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    listval.push(color);
    color = "#";
    
  }
  return listval;
 
  
}

const chart2 = (data)=>{
  let value = Array()
  let label = Array()
  for (var i in data){
    value.push(data[i][0])
    label.push(data[i][1])

  }
  
  const data1 = {
    labels: label,
    datasets: [{
      label:"data",
      backgroundColor: getRandomColor(label.length),
      data: value,
    }]
  };
  const config2 = {
    type: 'bar',
    data: data1,
    options: {}
  };
  
  
  const myChart2 = new Chart(
    document.getElementById('purchased'),
    config2
);

$('#purchased_values').append("<h2>"+label.length+"</h2>");
  

for(var q in label){
let h = `
<div class = 'row'>
  <div class="col">
    <div class="chart" >
      <h5>${label[q]}</h5>
    </div>
  </div>
</div>

<div class="row">
  <div class="col">
     <canvas id="overview${q}"></canvas>
  </div>
  <div class="col">
    <canvas id="abc${q}"></canvas>
  </div>
</div>
`

$("#overview").append(h)


}
makeDynamicCharts(label)
}

const makeDynamicCharts = (label)=>
{
  $.ajax({
    type:"GET",
    url:"/usercourse",
    success: function(result){
    charts(label,result['data'])
    }
  });



  


const charts =(label,dataval)=>{

  for(var i in label)
  {
    let data = {
      labels: ['Tests','Modules'],
      datasets: [{
        label:"data",
        backgroundColor: getRandomColor(2),
        data:  dataval[0][i],
      }]
    };
    
    let data1 = {
      labels: [1,2,3,4,5,6,7,8,9,10],
      datasets: [{
        label: 'User Access Time  ',
        backgroundColor: getRandomColor(1) ,
        borderColor:getRandomColor(1) ,
        data: dataval[1][i],
      }]
    };
    const config2 = {
      type: 'line',
      data: data1,
      options: {}
    };

    const config1 = {
      type: 'doughnut',
      data: data,
      options: {}
    };
  

    new Chart( document.getElementById('overview'+i) , config1);
    new Chart( document.getElementById('abc'+i), config2 );
  }
} 
}
