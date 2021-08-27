$(document).ready(function () {
	$.ajax({url: "/saas/check_space", type:"post", dataType:"json", data:{}, async:false, success: function(result){
    	if (result.close) {
    		value = false
    		//$("#id_purchase_product_exist").show();
    		var $warning = $('<div style="z-index: 999999; width: inherit;height: 80px;margin-top:20px;margin-left:-20px;background-color:transparent" class="ui-popup alert" id="karma_alert_close_to_limit">'+
    			    		        ' Warning!</br>You are reaching to your data size limit, please consider buying an additional space. Your remaining space is arround 200MB. </div>');
		    
		    	$(".oe_login_buttons").parent().append($warning);	
		    
    	}
    }
	});
	

//----------------Onclick of Log in button validate email field--------------- 

$(".oe_login_buttons").click(function (event) {
	var value = true;
    $.ajax({url: "/saas/check_space", type:"post", dataType:"json", data:{}, async:false, success: function(result){
    	if (result.flag) {
    		value = false
    		var $warning = $('<div style="z-index: 999999; width: inherit;height: 80px;margin-top:20px;color:red;background-color:gray" class="ui-popup alert" id="karma_alert_db_limit">'+
    			    		        ' You reached at your database space limit, please buy extra space to continue the services </div>');
		    	if(document.getElementById('karma_alert_close_to_limit')){
		    		document.getElementById("karma_alert_close_to_limit").remove();
		    	}
		    	if(document.getElementById('karma_alert_db_limit')){
		    		document.getElementById("karma_alert_db_limit").remove();
		    	}
		    	$(".oe_login_buttons").parent().append($warning);	
		    
    	}
    }
	});
	return value
});


});




