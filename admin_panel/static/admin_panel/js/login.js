  document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.tap-target');
    var instances = M.TapTarget.init(elems, {});
  });

    var button = document.getElementById('help-button');
    button.addEventListener('click', function () {
         var menuItem = document.querySelectorAll('.tap-target');
         var instance = M.TapTarget.getInstance(menuItem[0]);
         instance.open();
    })