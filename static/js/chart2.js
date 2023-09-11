


const useruptime = ()=>{
    $.ajax({
      type: "POST",
      url: "/alluseraccess",
      success: function(result) {
        chart1(result['data'])
      } 
    });
}


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
        data: data1[0],
      }]
    };
    const config = {
      type: 'line',
      data: data,
      options: {}
    };
  
    const myChart1 = new Chart(
      document.getElementById('alluserlogin'),
      config
  );
   $("#totaluser").html(data1[1]+" users")
  }
  
  