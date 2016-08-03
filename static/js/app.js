function showLoggedInStatus() {
    $.mobile.loading( "show" );
    $.getJSON("/isloggedin", function( data ) {
        console.log(data);
        if(data.isLoggedIn) {
            $("#loginLink").hide();
            $("#registerLink").hide();

            $.getJSON("/getuser", function( data ) {
                $("#userName").html(data.firstName);
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

$(document).on('click', '#loginSubmitBtn', function() {
    $.mobile.loading( "show" );
    $("#posturl").val("/verifyFactor");
    $.post( "/login", $("#loginForm").serialize(), function( data ) {
        $("#floatingLogin").popup("close");
        console.log(data);
        results = JSON.parse(data);
        $("#refurl").val(results._links.verify.href);
        $("#floatingFactorVerification").popup();
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
    $("#floatingLogin").on("popupafterclose", openFactorVerificationPopup);
    $("#floatingRegister").on("popupafterclose", openFactorVerificationPopup);
});

$(document).ready(function() {
    showLoggedInStatus();
});