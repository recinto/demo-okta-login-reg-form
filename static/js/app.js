function showLoggedInStatus() {
    $.mobile.loading( "show" );
    $.getJSON("/isloggedin", function( data ) {
        console.log(data);
        if(data.isLoggedIn) {
            $("#loginLink").hide();
            $("#registerLink").hide();

            $.getJSON("/getuser", function( data ) {
                console.log(data);
                $("#userName").html(data.firstName);
                renderMemberRecords(data.hpsMemberRecords);
                $("#displayName").show();
                $.mobile.loading( "hide" );
            });
        } else {
            $("#loginLink").show();
            $("#registerLink").show();
            $("#displayName").hide();
            $.mobile.loading( "hide" );
        }
    });
}

function openFactorVerificationPopup() {
    setTimeout(function(){
        $("#floatingFactorVerification").popup("open");
        console.log("TIMEOUT");
    }, 50 );
}

function createSession() {
    console.log("create session");
    $.getJSON("/createsession", function( data ) {
        console.log(data);
        if(data.success) {
            showLoggedInStatus();
        }
    });
}

function renderMemberRecords(memberRecordList) {
    var output = "No Member Records Assigned"
    if(memberRecordList) {
        if(memberRecordList.length > 0) {
            if(memberRecordList[0] != "") {
                output = "";
                for(var i = 0; i < memberRecordList.length; i++) {
                    output += memberRecordList[i] + "<br />";
                }
            }
        }
    }

    $("#memberRecordList").html(output);
}

$(document).on('click', '#loginSubmitBtn', function() {
    $.mobile.loading( "show" );
    $("#posturl").val("/verifyFactor");
    $.post( "/login", $("#loginForm").serialize(), function( data ) {
        $("#floatingLogin").popup("close");
        console.log(data);
        results = JSON.parse(data);
        if(results._links.verify) {
            $("#refurl").val(results._links.verify.href);
        }
        openFactorVerificationPopup();
    }).done(function() {
        console.log( "done" );
    }).fail(function() {
        console.log( "error" );
    }).always(function() {
        console.log( "finished" );
        $.mobile.loading( "hide" );
    });
});

$(document).on('click', '#factorVerificationSubmitBtn', function() {
    $.mobile.loading( "show" );
    $.post( $("#posturl").val(), $("#factorVerificationForm").serialize(), function( data ) {
        console.log(data);
        results = JSON.parse(data);

        if("SUCCESS"==results.factorResult) {
            $("#floatingFactorVerification").popup("close");
            if("/activate" == $("#posturl").val()) {
                console.log("call create session");
                createSession();
            } else {
                console.log("show logged in status");
                showLoggedInStatus();
            }
        }
    }).done(function() {
        console.log( "done" );
    }).fail(function() {
        console.log( "error" );
    }).always(function() {
        console.log( "finished" );
        $.mobile.loading( "hide" );
    });
});

$(document).on('click', '#registerSubmitBtn', function() {
    $.mobile.loading( "show" );
    $("#posturl").val("/activate");
    //TODO: Perform validation here

    $.post( "/register", $("#registraionForm").serialize(), function( data ) {
        $("#floatingRegister").popup("close");
        console.log(data);
        results = JSON.parse(data);
        $("#refurl").val(results._links.activate.href);
        openFactorVerificationPopup();
    }).done(function() {
        console.log( "done" );
    }).fail(function() {
        console.log( "error" );
    }).always(function() {
        console.log( "finished" );
        $.mobile.loading( "hide" );
    });
});

$( document ).bind ("pageinit", function() {
    $("#floatingFactorVerification").popup();
});

$(document).ready(function() {
    showLoggedInStatus();
});