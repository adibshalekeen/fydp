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
document.getElementsByClassName('update-saved-devices')[0].addEventListener('click', update_saved_devices, false);

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
var searchTimeElapsed;

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
  if(address)
  {
    this.innerHTML = (address) ? address.toUpperCase() : ".";
    if($(this)[0].parentNode.parentNode.id.indexOf("map") >= 0)
    {
      document.getElementsByClassName("save-mappings")[0].classList.remove("disabled_button");
    }
    else if($(this)[0].parentNode.parentNode.id.indexOf("act") >= 0 )
    {
      document.getElementsByClassName("save-actions")[0].classList.remove("disabled_button");
    }
  }
}

function autoAdd()
{
  var result = confirm("Would you like to save this device? \
                    \nBe sure to load the current saved mapping first.");

  if(result)
  {
    //document.getElementsByClassName("load-mappings")[0].click();
    var deviceData = $(this)[0].parentElement.innerText.split(/\s+/).slice(0, 2);
    add_row("mapping-table", true, deviceData);
    document.getElementsByClassName("save-mappings")[0].classList.remove("disabled_button");
    var clickable_items = document.getElementsByClassName('clickable');
    for (var i = 0; i < clickable_items.length; i++) {
        clickable_items[i].addEventListener('click', clickResp, false);
        clickable_items[i].addEventListener('dblclick', dblClickResp, false);
    }
  }
}

// Make table function
function make_table(items, element_id, clickable)
{
  item_class = (clickable) ? "table-column clickable" : "table-column";
  item_class = (element_id.indexOf("device") >= 0) ? "table-column auto-add" : item_class;
  var html = "";
  var columns = (element_id.indexOf("mapping") >= 0) ? 3 : 4;

  for( var i = 0; i < items.length; i++)
  {
    items[i] = items[i].replace(/_/g, " ");

    if(i % columns === 0)
    {
      html += "<tr><td class=\"" + item_class + "\">";
    }
    else if(i % columns === columns - 1)
    {
      html += "</td><td class=\"" + item_class + "\">";
      html += items[i];
      html += "</td></tr>";
      continue;
    }
    else
    {
      html += "</td><td class=\"" + item_class + "\">";
    }
    html += items[i];
  }
  document.getElementById(element_id).innerHTML = html;
}

function add_row(element_id, clickable, fields = null)
{
  var html = "";
  item_class = (clickable) ? "table-column clickable" : "table-column";

  var columns = (element_id.indexOf("mapping") >= 0) ? 3 : 4;

  var content = [columns];
  // Fix this not displaying on the table
  var content = (fields) ? [".", fields[0], fields[1]] : Array(columns).fill(".");
  html += "<tr>";
  for( var i = 0; i < columns; i++)
  {
    html += "<td class=\"" + item_class + "\">" + content[i] + "</td>";
  }
  html += "</tr>";
  document.getElementById(element_id).innerHTML += html;
}

function displayElapsedTime()
{
  var timeElapsed = 1;
  var message = "";

  searchTimeElapsed = setInterval(function displayTime() {
    message = "Elapsed Time: " + timeElapsed + "s";
    document.getElementById("device-table").innerHTML = message;
    timeElapsed += 1;
  }, 1000);
}

function display_devices()
{
  var thisClass = $(this);
  displayElapsedTime();
  document.getElementById("device-table").innerHTML = "";
  thisClass.addClass('disabled_button');
  //var items = ["10.20.138.31", "24:18:1D:5C:67:7D", "v1020-wn-138-31.campus-dynamic.uwaterloo.ca", "Unknown", "10.20.138.35", "24:18:1D:5C:67:7E", "v1020-wn-138-31.campus-dynamic.uwaterloo.ca", "Unknown"];
  var items = [];
  $.ajax({
    url:"http://localhost:2081/getDevices",
    type: "GET",
    success: function(items){
       thisClass.removeClass('disabled_button');
       make_table(items, "device-table", false);
       clearInterval(searchTimeElapsed);

       var clickable_items = document.getElementsByClassName('auto-add');
       for (var i = 0; i < clickable_items.length; i++) {
          clickable_items[i].addEventListener('dblclick', autoAdd, false);
       }
       document.getElementsByClassName("update-saved-devices")[0].classList.remove("disabled_button");
    },
    error: function(err){
      console.log(err);
    }
  })
}

function update_saved_devices()
{
  var devices_array = [];
  var devices_table = $("#device-table").children();
  for(var i = 0; i < devices_table.length; i++)
  {
    var row = devices_table[i].innerText;
    row = row.replace(/ /g, "_");
    var values = row.split(/\s+/);
    devices_array.push(values);
  }

  var mapping_array = [];
  var mapping_table = $("#mapping-table").children();
  for(var i = 0; i < mapping_table.length; i++)
  {
    var row = mapping_table[i].innerText;
    row = row.replace(/ /g, "_");
    var values = row.split(/\s+/);

    for(var j = 0; j < devices_array.length; j++)
    {
      if(devices_array[j][1] == values[2])
      {
        values[1] = devices_array[j][0];
      }
    }
    mapping_array.push(values);
  }

  make_table(mapping_array.flat(), "mapping-table", true);
  document.getElementsByClassName("save-mappings")[0].classList.remove("disabled_button");
  document.getElementsByClassName("update-saved-devices")[0].classList.add("disabled_button");
  var clickable_items = document.getElementsByClassName('clickable');
  for (var i = 0; i < clickable_items.length; i++) {
      clickable_items[i].addEventListener('click', clickResp, false);
      clickable_items[i].addEventListener('dblclick', dblClickResp, false);
  }
}

function load_device_mappings()
{
  var table = ""
  if($(this)[0].classList[1].indexOf("mapping") >= 0)
  {
    table = "mapping-table";
    document.getElementsByClassName("save-mappings")[0].classList.add("disabled_button");
  }
  else if($(this)[0].classList[1].indexOf("action") >= 0)
  {
    table = "action-table"
    document.getElementsByClassName("save-actions")[0].classList.add("disabled_button");
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
    document.getElementsByClassName("save-mappings")[0].classList.remove("disabled_button");
  }
  else if($(this)[0].classList[1].indexOf("action") >= 0)
  {
    table = "action-table"
    document.getElementsByClassName("save-actions")[0].classList.remove("disabled_button");
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

  var disable_btn = (delete_req == "map") ? "save-mappings" : "save-actions";
  document.getElementsByClassName(disable_btn)[0].classList.remove("disabled_button");

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
    document.getElementsByClassName("save-mappings")[0].classList.add("disabled_button");
  }
  else if($(this)[0].classList[1].indexOf("action") >= 0)
  {
    table = "action-table"
    document.getElementsByClassName("save-actions")[0].classList.add("disabled_button");
  }

  var mapping_array = "";
  var mapping_table = $("#"+table).children();
  for(var i = 0; i < mapping_table.length; i++)
  {
    var row = mapping_table[i].innerText;
    row = row.replace(/ /g, "_");
    console.log(row);
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
