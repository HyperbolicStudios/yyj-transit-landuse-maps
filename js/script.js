jQuery(document).on("keypress", 'form', function (e) {
    var code = e.keyCode || e.which;
    if (code == 13) {
        e.preventDefault();
        return false;
    }
});

function openNav() {
  document.getElementById("menu").style.transform = "translateX(0)";
  console.log("open");
}

function closeNav() {
  document.getElementById("menu").style.transform = "translateX(100%)";
}

function update() {
  document.getElementById('igraph').src += '';
  console.log("updated");
}

function updateMap(id,special) {
var e = document.getElementById(id);
var value = e.value;
console.log(value);
if (special) {
  $("#main-title").text("Zoning within 400m of " + value + " stops");
}
else {
  $("#main-title").text("Zoning within 400m of route " + value + " stops");
}
$("#map").attr("src","charts/"+value+".html");
}
