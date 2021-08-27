odoo.define('saas_product.manage_database', function(require) {
	"use strict";
	var ajax = require('web.ajax');
	$(document).ready(function() {
		$("#save_users").hide();
	})
	
	
	//Start
	$(function() {
		$('#save_user').on('click', function() {
			console.log("yes!!!")
			var db_name = $('#db_name_xml').text()
			var user_count = $('#num_user').val()
			
			if (parseInt(user_count) < 0){
				alert("Value should be more than zero")
				return false
			}

			$.ajax({
				url : '/apps/add_more_users',
				type : 'POST',
				async : false,
				data : {
					db : db_name,
					users : user_count
				},
				success : function(data) {
					$("#save_users").hide();
					$("#update_user").show();
					$("#show_user").show();
					$("#update_user").text(data);
					$("#update_user2").text(data);

				},
				failure : function(data) {
					alert("Some Error!!")
				}
			})

		})

	})//End


	
	//Start
	$(function() {
		$('.deact').on('click', function() {
			var login = $(this).attr('login');
			var db = $(this).attr('db');
			$.ajax({
				url : '/apps/remove_users',
				type : 'POST',
				async : false,
				data : {
					user : login,
					db : db
				},
				success : function(data) {
					location.reload();

				},
				failure : function(data) {
				}
			})

		})
	})
	//End
	
	//Start
	$(function() {
		$('.react').on('click', function() {
			var self = this
			var login = $(this).attr('login');
			var db = $(this).attr('db');
			$.ajax({
				url : '/apps/activate_user_again',
				type : 'POST',
				async : false,
				data : {
					user : login,
					db : db
				},
				success : function(data) {
					var res = JSON.parse(data)
					console.log('=========================================')
					console.log(res)
					console.log(res.allow)
					console.log(res['allow'])
					console.log('++++++++++++++++++++++++++++')
					if (res.allow == true){
						location.reload();
					}
					else{
						$(self).parent().append("<p><font color='red' >Can't activate more than Purchased Users</font></p>")
					}

				},
				failure : function(data) {
				}
			})

		})
	})//End
	
	
	
	//Start
	$(function() {
		$('#show_user').on('click', function() {
			$("#save_users").show();
			$("#add_text_id").show();

			$("#update_user").hide();
			$("#show_user").hide();

		})
	})//End

	
	//Start
	$(function() {
		$('#id_cancel').on('click', function() {
			$("#save_users").hide();
			$("#update_user").show();
			$("#add_text_id").hide();
			$("#show_user").show();

		})
	})

})