function openNavMenu() {
    document.getElementById("navMenu").classList.toggle("show");
}

function openAccountMenu() {
  document.getElementById("accountMenu").classList.toggle("show");
}
function closeDropDown(menu) {
  var dropdowns = document.getElementsByClassName(menu);
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
}
// Close the dropdown if the user clicks outside of it
window.onclick = function(event) {
  if (!event.target.matches('#userButton')) {
    this.closeDropDown("accDropList");
  }
  if (!event.target.matches('#navButton')) {
    this.closeDropDown("navDropList");
  }
}
window.onresize = function(event) {
  if (window.innerWidth >= 1350) {
    this.closeDropDown("navDropList");
  }
}