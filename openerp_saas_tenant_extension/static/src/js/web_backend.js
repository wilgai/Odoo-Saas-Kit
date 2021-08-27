odoo.define('openerp_saas_tenant_extension.web_backend', function (require) {
    "use strict";

    require('web.dom_ready');
    var base = require("web_editor.base");
    var ajax = require('web.ajax');
    var ajax = require('web.ajax');
    
//    ajax.jsonRpc("/web/check_for_superuser", 'call', {}).then(
//        	var num = parseInt(result.user)
//        	if (num !=1){
//        		alert(3);
//        		$('.o_web_settings_dashboard_apps').hide()
//        	}
//        })
        
})





/// Remove browse apps from Settings dashboard for Tenant Users
//function waitForElement(elementPath, callBack){
//  window.setTimeout(function(){
//    if($(elementPath).length){
//      callBack(elementPath, $(elementPath));
//   }else{
//      waitForElement(elementPath, callBack);
//    }
//  },500)
//}


//waitForElement(".o_web_settings_dashboard_apps",function(){
//	$.ajax({url: "/web/check_for_superuser", type:"post", dataType:"json", data:{}, async:false, success: function(result){
//    	var num = parseInt(result.user)
//    	if (num !=1){
//    		$('.o_web_settings_dashboard_apps').delay(3000).hide()
//    	}
//}
//});
//});



