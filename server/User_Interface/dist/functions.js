/********************************************************************************/
/*                         EVENT LISTENER DECLARATION                           */
/********************************************************************************/
// Prevent scrolling when the mouse is hovered over the data boxes for user
// experience boost!
var fixed = document.getElementsByClassName('fixed');
for (var i = 0; i < fixed.length; i++) {
    fixed[i].addEventListener('mousewheel', function(e) {
      e.preventDefault();
    }, false);
}

// Event handler for populating device list
document.getElementsByClassName('find-devices')[0].addEventListener('click', display_devices, false);

// Event handler for device mappings list
document.getElementsByClassName('load-mappings')[0].addEventListener('click', load_device_mappings, false);
document.getElementsByClassName('add-mapping')[0].addEventListener('click', add_device_mapping, false);
document.getElementsByClassName('delete-mapping')[0].addEventListener('click', delete_device_mapping, false);
document.getElementsByClassName('save-mappings')[0].addEventListener('click', save_device_mappings, false);

// Event handler for action mappings list
document.getElementsByClassName('load-actions')[0].addEventListener('click', load_device_mappings, false);
document.getElementsByClassName('add-action')[0].addEventListener('click', add_device_mapping, false);
document.getElementsByClassName('delete-action')[0].addEventListener('click', delete_device_mapping, false);
document.getElementsByClassName('save-actions')[0].addEventListener('click', save_device_mappings, false);

/********************************************************************************/
/*                         CALLBACK FUNCTION DECLARATION                        */
/********************************************************************************/
function clickResp()
{
  var clicked_btn = document.getElementsByClassName("clicked");
  if(clicked_btn.length)
  {
    document.getElementsByClassName("clicked")[0].classList.remove("clicked");
  }
  $(this)[0].parentNode.classList.add("clicked");
}

function dblClickResp()
{
  var address = prompt("Please enter the new value", this.innerHTML);
  this.innerHTML = (address) ? address.toUpperCase() : this.innerHTML;
}

// Make table function
function make_table(items, element_id, clickable)
{
  item_class = (clickable) ? "table-column clickable" : "table-column";
  var html = "";
  for( var i = 0; i < items.length; i++)
  {
    if(i % 4 === 0)
    {
      html += "<tr><td class=\"" + item_class + "\">";
      html += items[i];
    }
    else if(i % 4 === 1)
    {
      html += "</td><td class=\"" + item_class + "\">";
      html += items[i];
    }
    else if(i % 4 === 2)
    {
      html += "</td><td class=\"" + item_class + "\">";
      html += items[i];
    }
    else if(i % 4 === 3)
    {
      html += "</td><td class=\"" + item_class + "\">";
      html += items[i];
      html += "</td></tr>";
    }
  }
  document.getElementById(element_id).innerHTML = html;
}

function add_row(element_id, clickable)
{
  var html = "";
  item_class = (clickable) ? "table-column clickable" : "table-column";
  html += "<tr><td class=\"" + item_class + "\">";
  html += "</td><td class=\"" + item_class + "\">";
  html += "</td><td class=\"" + item_class + "\">";
  html += "</td><td class=\"" + item_class + "\">";
  html += "</td></tr>";

  document.getElementById(element_id).innerHTML += html;
}

function display_devices()
{
  var thisClass = $(this);
  document.getElementById("device-table").innerHTML = "";
  thisClass.addClass('disabled_button');
  var items = [];
  $.ajax({
    url:"http://localhost:2081/getDevices",
    type: "GET",
    success: function(items){
      thisClass.removeClass('disabled_button');
      make_table(items, "device-table", false);
    },
    error: function(err){
      console.log(err);
    }
  })
}

function load_device_mappings()
{
  var table = ""
  if($(this)[0].classList[1].indexOf("mapping") >= 0)
  {
    table = "mapping-table";
  }
  else if($(this)[0].classList[1].indexOf("action") >= 0)
  {
    table = "action-table"
  }

  var items = [];
  $.ajax({
    url:"http://localhost:2081/getMappings",
    type: "POST",
    data: table,
    success: function(items){
      make_table(items, table, true);

      var clickable_items = document.getElementsByClassName('clickable');
      for (var i = 0; i < clickable_items.length; i++) {
          clickable_items[i].addEventListener('click', clickResp, false);
          clickable_items[i].addEventListener('dblclick', dblClickResp, false);
      }
    },
    error: function(err){
      console.log(err);
    }
  })
}

function add_device_mapping()
{
  var table = ""
  if($(this)[0].classList[1].indexOf("mapping") >= 0)
  {
    table = "mapping-table";
  }
  else if($(this)[0].classList[1].indexOf("action") >= 0)
  {
    table = "action-table"
  }
  add_row(table, true);

  var clickable_items = document.getElementsByClassName('clickable');
  for (var i = 0; i < clickable_items.length; i++) {
      clickable_items[i].addEventListener('click', clickResp, false);
      clickable_items[i].addEventListener('dblclick', dblClickResp, false);
  }
}

function delete_device_mapping()
{
  var delete_req = ($(this)[0].classList.value.indexOf("map") >= 0) ? "map" : "act";
  var clicked_btn = document.getElementsByClassName("clicked");
  var delete_req_parent = clicked_btn[0].parentNode.id;
  if(clicked_btn.length && (delete_req_parent.indexOf(delete_req) >= 0))
  {
    var parent = clicked_btn[0].parentNode.removeChild(clicked_btn[0]);
  }
}

function save_device_mappings()
{
  if(!confirm('Saving will overwrite the current file. Are you sure?'))
    return;

  var table = ""
  if($(this)[0].classList[1].indexOf("mapping") >= 0)
  {
    table = "mapping-table";
  }
  else if($(this)[0].classList[1].indexOf("action") >= 0)
  {
    table = "action-table"
  }

  var mapping_array = "";
  var mapping_table = $("#"+table).children();
  for(var i = 0; i < mapping_table.length; i++)
  {
    var row = mapping_table[i].innerText;
    var values = row.split(/\s+/);
    mapping_array += values + "|";
  }
  mapping_array += (table === "mapping-table") ? "map" : "act";
  $.ajax({
    type: "POST",
    url: "http://localhost:2081/saveMappings",
    data: mapping_array,
    success: function(){
    }
  });
}
