//variable containing reference to data
var data;

//D3.js canvases
var textArea;
var barChartArea;
var heatMap;

//D3.js svg elements
var selectedAreaText;

//variables for selection
var selectedRegion;

/*Loading data from CSV file and editing the properties to province codes. Unary operator plus is used to save the data as numbers (originally imported as string)*/
d3.csv("./public/data.csv")
  .row(function (d) {
    return {
      date: d.Date,
      Argentina: +d.Argentina,
      Buenos_Aires: +d["Buenos Aires"],
      La_Pampa: +d["La Pampa"],
      Mendoza: +d.Mendoza,
      Santa_Fe: +d["Santa Fe"],
      Córdoba: +d.Córdoba
    };
  }).get(function (error, rows) {
    //saving reference to data
    data = rows;

    //load map and initialise the views
    init();

    // data visualization
    visualization();
  });

/*----------------------
INITIALIZE VISUALIZATION
----------------------*/
function init() {

  let width = screen.width;
  let height = screen.height;

  //retrieve a SVG file via d3.request, 
  //the xhr.responseXML property is a document instance
  function responseCallback(xhr) {
    d3.select("#map_div").append(function () {
      return xhr.responseXML.querySelector('svg');
    }).attr("id", "map")
      .attr("width", width / 4)
      .attr("height", height - 100)
      .attr("x", 0)
      .attr("y", 0);
  };

  //You can select the root <svg> and append it directly
  d3.request("public/ar.svg")
    .mimeType("image/svg+xml")
    .response(responseCallback)
    .get(function (n) {
      let map = d3.select("body").select("#map");
      map.selectAll("path")
        .style("fill", "#000000")
        .style("stroke", "#3e4147")
        .on("click", function () {
          mapClick(this);
        });
    });

  //d3 canvases for svg elements
  textArea = d3.select("#text_div").append("svg")
    .attr("width", d3.select("#text_div").node().clientWidth)
    .attr("height", d3.select("#text_div").node().clientHeight);

  barChartArea = d3.select("#barchart_div").append("svg")
    .attr("width", d3.select("#barchart_div").node().clientWidth)
    .attr("height", d3.select("#barchart_div").node().clientHeight);

  heatMap = d3.select("#heatmap_div").append("svg")
    .attr("width", d3.select("#heatmap_div").node().clientWidth)
    .attr("height", d3.select("#heatmap_div").node().clientHeight);

  //init selections
  selectedRegion = 'Argentina';
}


/*----------------------
BEGINNING OF VISUALIZATION
----------------------*/
function visualization() {

  drawTextInfo();

  drawBarChart(selectedRegion);

  drawHeatMap();

}

/*----------------------
TASKS:
1) Create a bar chart of the number of ill people over the time in Argentina 
2) Create a heat map for all regions in the dataset
3) Connect SVG map with the bar chart
4) Animate bar chart transitions
----------------------*/

/*----------------------
TEXT INFORMATION
----------------------*/
function drawTextInfo() {
  //Draw headline
  textArea.append("text")
    .attrs({ dx: 20, dy: "1em", class: "headline" })
    .text("Graph of flu trends in Argentina");

  //Draw source
  textArea.append("text")
    .attrs({ dx: 20, dy: "3.5em", class: "subline" })
    .text("Data source: Google Flu Trends")
    .on("click", function () { window.open("http://www.google.org/flutrends"); });;

  //Draw selection information
  selectedAreaText = textArea.append("text")
    .attrs({ dx: 20, dy: "4.8em", class: "subline" })
    .text("Selected Region: " + selectedRegion);
}


/*----------------------
BAR CHART
----------------------*/
function drawBarChart(region) {
  barChartArea.remove();

  barChartArea = d3.select("#barchart_div").append("svg")
    .attr("width", d3.select("#barchart_div").node().clientWidth)
    .attr("height", d3.select("#barchart_div").node().clientHeight);

  let thisCanvasWidth = barChartArea.node().clientWidth;
  let thisCanvasHeight = barChartArea.node().clientHeight;

  //Width of all bars in barchart will be the same
  var barWidth = thisCanvasWidth / data.length;

  //For the height, we need to normalize the data first
  //We start with finding the highest value 
  var topValue = 0;
  for (let index = 0; index < data.length; index++) {
    if (topValue < data[index][region]) topValue = data[index][region];
  }
  console.log("Top globsl value from our data is: " + topValue)

  //Now for all the global records in our data, we will calculate heigth of individual bars
  //And then we can append a new rect to barChartArea canvas
  for (let index = 0; index < data.length; index++) {
    var barHeight = (data[index][region] / topValue) * thisCanvasHeight;
    barChartArea.append('rect')
      .attrs({ x: index * barWidth,
         y: thisCanvasHeight, 
         width: barWidth + 1, 
         height: barHeight, 
         fill: 'white' })
      .transition()
      .duration(500)
      .attrs({y: thisCanvasHeight - barHeight, height: barHeight});
         
  }

  //For year labels, we create a new string variable and check whether this value changed
  var year = "";
  for (let index = 0; index < data.length; index++) {
    //We can compare just first four chars of date string
    if (year != data[index].date.substr(0, 4)) {
      year = data[index].date.substr(0, 4);
      barChartArea.append("text")
        .attrs({ dx: index * barWidth, dy: thisCanvasHeight, class: "subline" })
        .style("Fill", "Black")
        .text(year);
    }
  }


  //Square example
  // barChartArea.append('rect')
  //          .attrs({ x: thisCanvasWidth/3, y: thisCanvasHeight/3, width: 80, height: 80, fill: 'red' })
  //          .transition()
  //          .duration(5000)
  //          .attrs({ x: 2*thisCanvasWidth/3, y: 2*thisCanvasHeight/3, width: 40, height: 40, fill: 'blue' });

}

/*----------------------
HEAT MAP
----------------------*/
function drawHeatMap() {
  let thisCanvasWidth = heatMap.node().clientWidth;
  let thisCanvasHeight = heatMap.node().clientHeight;

  var barWidth = thisCanvasWidth / data.length;
  var barHeight = thisCanvasHeight / Object.keys(data[0]).length - 1;

  var topValue = 0;
  for (let index = 0; index < data.length; index++) {
    for (var key in data[index]) {
      if (key != "date") {
        if (topValue < data[index][key]) topValue = data[index][key];
      }
    }
  }

  console.log("Top global value from our data is: " + topValue)
  // https://github.com/d3/d3-color
  for (let index = 0; index < data.length; index++) {
    var yPosition = 0;
    for (var key in data[index]) {
      var color = 0;
      if (key != "date") {
        heatMap.append('rect')
          .attrs({ x: index * barWidth, 
            y: yPosition, 
            width: barWidth, 
            height: barHeight, 
            fill: d3.rgb(data[index][key]/topValue * 255,0,0) })
        yPosition += barHeight;
      }
    }
  }



}

/*----------------------
INTERACTION
----------------------*/
function mapClick(region) {
  console.log(region.id)
  selectedRegion = (region.id.substr(0,3) == "ARG") ? 'Argentina': region.id;
  selectedAreaText.text("Selected Region: " + selectedRegion);

  drawBarChart(selectedRegion);

}






