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

function updateMap() {
var e = document.getElementById("route-selection");
var value = e.value;
console.log(value);
$("#map").attr("src","charts/"+value+".html");
}
