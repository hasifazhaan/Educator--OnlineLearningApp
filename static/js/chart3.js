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


$(document).ready(()=>{
    top10course()
})


const top10course = ()=>{
    $.ajax({
        type: "POST",
        url: "/top10course",
        success: function(result) {
          var values = result['data']
            const data = {
                labels:values[0],
                datasets: [{
                  label: 'User Purchased  ',
                  backgroundColor: getRandomColor(values[1].length),
                  borderColor: 'rgb(222, 4, 50)',
                  data: values[1],
                }]
              };
              const config = {
                type: 'bar',
                data: data,
                options: {}
              };
            
              new Chart(
                document.getElementById('topcourse'),
                config
            );
            topuser();
        } 
      });
    
}


const topuser = ()=>{
    $.ajax({
        type: "POST",
        url: "/topuser",
        success: function(result) {
         values = result['data']
         color = getRandomColor(values[1].length)
         const data1 = {
            labels:values[0],
            datasets: [{
              label: 'Hours',
              backgroundColor: color,
              borderColor:color ,
              data: values[1],
            }]
          };
          const config1 = {
            type: 'doughnut',
            data: data1,
            options: {}
          };
        
          new Chart(
            document.getElementById('activeuser'),
            config1);
            completed()
        } 
      });
}


const completed = ()=>{

    $.ajax({
        type: "POST",
        url: "/usercompleted",
        success: function(result) {
        
        values = result['data']

        for(var i in values){
            let users = `
              <tr>
                <td>${values[i][0]}</td>
                <td>${values[i][1]}</td>
              </tr>
        `
        $("#completeduser").append(users)
        }

        failed_modules();
        } 
        
      });

}


const failed_modules = ()=>{

  $.ajax({
    type: "POST",
    url: "/userfailed",
    success: function(result) {
      values = result['data'];
      console.log(values)
      
      color = getRandomColor(values[0].length)
         const data3 = {
            labels:values[0],
            datasets: [{
              label: values[2],
              backgroundColor: color,
              borderColor:color ,
              data: values[2],
            }]
          };
          const config3 = {
            type: 'doughnut',
            data: data3,
            options: {}
          };
        
          new Chart(
            document.getElementById('failedmodules'),
            config3);
            

            for(var i in values[1]){
              let tag = `
            <div class="label-vals">
              <div style="height: 25px; width:40px; background-color:${color[i]} ;"></div>
              <label> ${values[1][i]}</label> 
            </div>
            `
              $("#failed").append(tag)
            }
            

            
    } 
  });

}