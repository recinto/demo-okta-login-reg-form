
function getUsers(){
    $.mobile.loading( "show" );
    //$("#usertable tbody").append("<tr><td>YO</td><td>YO</td><td>YO</td><td>YO</td><td>YO</td></tr>").table( "refresh" ).trigger( "create" );
    $.getJSON("/admin/users", function( data ) {
        console.log(data);
        tableBody = $("#usertable tbody");
        for(key in data) {
            renderRow(tableBody, data[key]);
        }
        //tableBody.table( "refresh" ).trigger( "create" );

        $.mobile.loading( "hide" );
    });
}

function renderRow(tableBody, userData){

    var row = document.createElement("tr");

    row.id = "row_" + userData.id;

    addTD(row, "id", userData.id);
    addTD(row, "email", userData.profile.email);
    addTD(row, "firstName", userData.profile.firstName);
    addTD(row, "lastName", userData.profile.lastName);
    addTD(row, "mobilePhone", userData.profile.mobilePhone);
    addTD(row, "hpsMemberRecords", userData.profile.hpsMemberRecords ? userData.profile.hpsMemberRecords : "");
    addTD(row, "action", "<a href=\"javascript:editUser('" + userData.id + "')\">edit</a> | <a href=\"javascript:deleteUser('" + userData.id + "')\">deactivate</a>");

    tableBody.append(row.outerHTML);
}

function editUser(userId) {
    $("#editUserForm")[0].reset();

    $("#email").val($("#row_" + userId + "_email").html());
    $("#firstName").val($("#row_" + userId + "_firstName").html());
    $("#lastName").val($("#row_" + userId + "_lastName").html());
    $("#mobile").val($("#row_" + userId + "_mobilePhone").html());
    $("#hpsMemberRecords").val($("#row_" + userId + "_hpsMemberRecords").html());

    $("#_id").val($("#row_" + userId + "_id").html());
    $("#password").hide();

    $("#editUserPopup").popup("open");
}

function updateUser(userId) {
    $.mobile.loading( "show" );
    $.ajax( {url: "/admin/usersx/" + userId, type: 'POST', data: $("#editUserForm").serialize(), dataType : "json"
    }).done(function(data) {
        $("#editUserPopup").popup("close");
        console.log(data);
        //TODO: add better UX handling so as to not refresh the whole darn page
        location.reload();
    }).fail(function() {
        console.log( "error" );
    }).always(function() {
        console.log( "finished" );
        $.mobile.loading( "hide" );
    });
}

function deleteUser(userId) {
    if(confirm("Are you sure you want to deactivate this user?")) {
        $.mobile.loading( "show" );
        $.ajax( {url: "/admin/users/" + userId, type: 'DELETE', dataType : "json"
        }).done(function(data) {
            $("#editUserPopup").popup("close");
            console.log(data);
            $("#row_" + userId).remove();
        }).fail(function() {
            console.log( "error" );
        }).always(function() {
            console.log( "finished" );
            $.mobile.loading( "hide" );
        });
    }
}

function addTD(row, fieldName, html) {
    var td =  document.createElement("td");
    td.innerHTML = html;
    td.id = row.id + "_" + fieldName;
    row.appendChild(td);
}

$(document).on('click', '#editUserSubmitBtn', function() {
    $.mobile.loading( "show" );
    var url = "/admin/users";
    var userId = $("#_id").val();
    if(userId) {
        updateUser(userId);
    } else {
        $.post(url, $("#editUserForm").serialize(), function( data ) {
            $("#editUserPopup").popup("close");
            results = JSON.parse(data);
            console.log(results);
            tableBody = $("#usertable tbody");
            renderRow(tableBody, results);
        }).done(function() {
            console.log( "done" );
        }).fail(function() {
            console.log( "error" );
        }).always(function() {
            console.log( "finished" );
            $.mobile.loading( "hide" );
        });
    }
});

$(document).on('popupafterclose', '#editUserPopup', function() {
    $("#password").show();
    $("#editUserForm")[0].reset();
});

$(document).ready(function() {

    getUsers();
    console.log("Admin Loaded");

});