var directory, enable_style_switcher, default_settings;

jQuery(document).ready(function() {


	/* styler config */
	
	default_settings = {
		color: '#660000',
		pattern: 'none', 			/* 'pattern_0', 'pattern_1' ... 'pattern_15' or 'none'  -  you can use if layout isn't  'full-width' */
		bg: 'none', 				/* 'image_0',  'image_1'  ... 'image_3' or 'none'  -  you can use if layout isn't  'full-width' */
		layout: 'full-width', 		/* 'full-width', 'boxed', 'boxed-attached'  */
		topNavBarStyle: 'static', 	/* 'static', 'fixed'  */
		sideBarPosition: 'left', 	/* 'left', 'right'  */
		sideBarWidth: 'maxi' 		/* 'maxi', 'mini'  */
	}
	
	enable_style_switcher = true;  /* enable or disable style switcher */
	
	/* end styler config */
	
	
	

	
	default_settings.pattern = 'js/style-switcher/patterns/' + default_settings.pattern + '.png';
	default_settings.bg = 'js/style-switcher/images/' + default_settings.bg + '.jpg';
	
	if(jQuery('body').hasClass('admin')) {
		directory = '../';
	} else {
		directory = '';
	}
	
	
	jQuery('head').append('<script type="text/javascript" src="' + directory + 'js/style-switcher/jquery.cookie.js">');

	
	if(enable_style_switcher){
	
		var colors_count = 11;
		var patterns_count = 12;
		var images_count = 3;
		
		var template = '<div id="mtp-toggle" class="styler_bg_color"><i class="moon-droplet"></i></div><div id="mtp-wrapper" class="styler_border_color"><div id="mtp-header" class="styler_bg_color">Style Switcher</div><div id="mtp-content"><div class="mtp-content-title">Layout:</div><select class="mtp-layout-select"><option value="full-width">Full width</option><option value="boxed">Boxed</option><option value="boxed-attached">Boxed (attached)</option></select><div class="mtp-divider"></div><div class="mtp-content-title">Base color:</div><span class="mtp-primary-color styler_bg_color"></span><input type="text" value="#2773ae" class="mtp-color-field"><ul class="mtp-color clearfix"></ul><div class="clear"></div><div class="mtp-divider"></div><div class="mtp-content-title">Background pattern:</div><ul class="mtp-background-pattern clearfix"></ul><div class="mtp-divider"></div><div class="mtp-content-title">Background Image:</div><ul class="mtp-background-image clearfix"></ul><div class="admin_options"><div class="mtp-divider"></div><div class="mtp-content-title">Top Nav Bar Style</div><div class="options-link top-nav-bar-style"><a href="#" class="static">Static</a><a href="#" class="fixed">Fixed</a></div><div class="mtp-divider"></div><div class="mtp-content-title">Side Bar Position</div><div class="options-link sidebarOpt side-bar-position"><a href="#" class="left">Left</a><a href="#" class="right">Right</a></div><div class="mtp-divider"></div><div class="mtp-content-title">Side Bar Width</div><div class="options-link sidebarOpt side-bar-width"><a href="#" class="mini">Mini</a><a href="#" class="maxi">Maxi</a></div></div></div></div>';
		
		jQuery('#container').append(template);
		
		
		jQuery('head').append('<link type="text/css" rel="stylesheet" href="' + directory + 'js/style-switcher/styler.css"/><script type="text/javascript" src="' + directory + 'js/style-switcher/iris.min.js"></script>');
		
		for(var i = 0; i < colors_count; i++){
			jQuery("#mtp-wrapper .mtp-color").append('<li class="color_' + i + '"></li>')
		}
		for(var i = 0; i < patterns_count; i++){
			jQuery("#mtp-wrapper .mtp-background-pattern").append('<li class="pattern_' + i + '"></li>')
		}
		for(var i = 0; i < images_count; i++){
			jQuery("#mtp-wrapper .mtp-background-image").append('<li class="image_' + i + '"></li>')
		}
		
		colorSwitcherPosition();
		
		var initStyler = getThemeSettings();
		if(initStyler) {
			colorPicker(initStyler.color);
		} 

		
		jQuery('.mtp-background-pattern li').click(function(){
			if (jQuery('.mtp-layout-select').val() == 'full-width'){
				alert('Please select "Boxed" layout!')
			} else {
				var selectedPattern = jQuery(this).attr('class'),
				patternUrl = 'js/style-switcher/patterns/' + selectedPattern + '.png';
				jQuery('body').css('background-image', 'url('+ directory + patternUrl +')').removeClass('background-cover').addClass('background-pattern');
				setThemeSettings('pattern', patternUrl);
			}
			
		});	
		
		jQuery('.mtp-background-image li').click(function(){
			if (jQuery('.mtp-layout-select').val() == 'full-width'){
				alert('Please select "Boxed" layout!')
			} else {
				var selectedImg = jQuery(this).attr('class'),
				imgUrl =  'js/style-switcher/images/' + selectedImg + '.jpg';
				jQuery('body').css('background-image', 'url('+ directory + imgUrl +')').removeClass('background-pattern').addClass('background-cover');
				setThemeSettings('bg', imgUrl);
			}
		});	
		jQuery('#mtp-toggle').click(function(e){
			if(jQuery(this).is('.mtp-toggle-close')){
				jQuery('#mtp-wrapper, #mtp-toggle').stop(true, true).animate({'right': '-200px'}, 300);
				setTimeout(function(){
					jQuery('#mtp-toggle').toggleClass('mtp-toggle-close');
				}, 500)
			} else {
				jQuery('#mtp-wrapper, #mtp-toggle').stop(true, true).animate({'right': 0}, 300);
				jQuery('#mtp-toggle').toggleClass('mtp-toggle-close');
			}
			e.stopPropagation();
		});
		jQuery('body').click(function(){
			if(jQuery('#mtp-toggle').is('.mtp-toggle-close')){
				jQuery('#mtp-wrapper, #mtp-toggle').stop(true, true).animate({'right': '-200px'}, 300);
				setTimeout(function(){
					jQuery('#mtp-toggle').toggleClass('mtp-toggle-close');
				}, 500)
			} 
		})
		jQuery('#mtp-wrapper').click(function(e){
			e.stopPropagation();
		})
		
		jQuery('.mtp-layout-select').change(function(){
			var currentClass = jQuery('#container').attr('class');
			jQuery('#container').removeClass(currentClass).addClass(jQuery(this).val());
			currentClass = jQuery(this).val();
			setThemeSettings('layout', currentClass);
			jQuery(window).trigger('resize');
		});
		
		jQuery('.mtp-primary-color').click(function(){
			jQuery('.iris-picker').toggle();
		});
			
		
		
		jQuery(".mtp-color li").click(function(){
			var color = rgb2hex(jQuery(this).css('background-color'));	
			setThemeSettings('color', color);
			changeColor(color);
			jQuery(".mtp-color-field").val(color);
			jQuery('.mtp-color-field').iris('color', color);
		})
		
		jQuery('.top-nav-bar-style a.static').on('click', function(e) {
			e.preventDefault();
			jQuery(this).addClass('active').siblings('a').removeClass('active');
			jQuery('body').removeClass('padTop44');
			jQuery('#top .navbar').removeClass('navbar-fixed-top').addClass('navbar-static-top');
			setThemeSettings('topNavBarStyle', 'static');
		});
		jQuery('.top-nav-bar-style a.fixed').on('click', function(e) {
			e.preventDefault();
			jQuery(this).addClass('active').siblings('a').removeClass('active');
			jQuery('body').addClass('padTop44');
			jQuery('#top .navbar').removeClass('navbar-static-top').addClass('navbar-fixed-top');
			setThemeSettings('topNavBarStyle', 'fixed');
		});
		jQuery('.side-bar-position a.left').on('click', function(e) {
			e.preventDefault();
			jQuery(this).addClass('active').siblings('a').removeClass('active');
			jQuery('body').removeClass('side-right');
			jQuery('#sidebarPos').addClass('');
			setThemeSettings('sideBarPosition', 'left');
		});
		jQuery('.side-bar-position a.right').on('click', function(e) {
			e.preventDefault();
			jQuery(this).addClass('active').siblings('a').removeClass('active');
			jQuery('body').addClass('side-right');
			setThemeSettings('sideBarPosition', 'right');
		});
		jQuery('.side-bar-width a.mini').on('click', function(e) {
			e.preventDefault();
			jQuery(this).addClass('active').siblings('a').removeClass('active');
			jQuery('body').addClass('mini-sidebar');
			setThemeSettings('sideBarWidth', 'mini');
		});
		jQuery('.side-bar-width a.maxi').on('click', function(e) {
			e.preventDefault();
			jQuery(this).addClass('active').siblings('a').removeClass('active');
			jQuery('body').removeClass('mini-sidebar');
			setThemeSettings('sideBarWidth', 'maxi');
		});
	} else {
		var initStyler = getThemeSettings();
		jQuery.cookie('themeSettings', null, { path: '/' });
	}

})
function setThemeSettings(key, value){
	var themeSettings = jQuery.parseJSON(jQuery.cookie('themeSettings')); 
	
	if(!themeSettings) themeSettings = {};
	
	themeSettings[key] = value;
	if(key == 'pattern') themeSettings['bg'] = '';
	if(key == 'bg') themeSettings['pattern'] = '';
	
	var s = JSON.stringify(themeSettings);
	jQuery.cookie('themeSettings', s, { path: '/' });
}

function getThemeSettings(){
	if(enable_style_switcher){
		var themeSettings = jQuery.parseJSON(jQuery.cookie('themeSettings')); 
	} else {
		var themeSettings = default_settings;
	}
	if(!themeSettings) themeSettings = default_settings;
	
	if(themeSettings.bg && themeSettings.bg != 'none' && themeSettings.layout != 'full-width'){
		jQuery('body').css('background-image', 'url('+ directory + themeSettings.bg +')').removeClass('background-pattern').addClass('background-cover');
	} else if(themeSettings.pattern && themeSettings.pattern != 'none' && themeSettings.layout != 'full-width'){
		jQuery('body').css('background-image', 'url('+ directory + themeSettings.pattern +')').removeClass('background-cover').addClass('background-pattern');
	} else {
		jQuery('body').removeClass('background-pattern background-cover').css('background', '#fff');
	}
	if(themeSettings.layout) {
		var currentClass = jQuery('#container').attr('class');
		jQuery('#container').removeClass(currentClass).addClass(themeSettings.layout);
		jQuery('.mtp-layout-select option[value="' + themeSettings.layout + '"]').attr('selected', true).siblings().removeAttr('selected');
	}
	if(themeSettings.color) changeColor(themeSettings.color); 
	
	if(themeSettings.topNavBarStyle == 'fixed') {
		jQuery('.top-nav-bar-style a.fixed').addClass('active').siblings('a').removeClass('active');
		jQuery('body').addClass('padTop44');
		jQuery('#top .navbar').removeClass('navbar-static-top').addClass('navbar-fixed-top');
	} else {
		jQuery('.top-nav-bar-style a.static').addClass('active').siblings('a').removeClass('active');
		jQuery('body').removeClass('padTop44');
		jQuery('#top .navbar').removeClass('navbar-fixed-top').addClass('navbar-static-top');
	}
	if(themeSettings.sideBarPosition == 'right') {
		jQuery('.side-bar-position a.right').addClass('active').siblings('a').removeClass('active');
		jQuery('body').addClass('side-right');
	} else {
		jQuery('.side-bar-position a.left').addClass('active').siblings('a').removeClass('active');
		jQuery('body').removeClass('side-right');
		jQuery('#sidebarPos').addClass('');
	}
	if(themeSettings.sideBarWidth == 'mini') {
		jQuery('.side-bar-width a.mini').addClass('active').siblings('a').removeClass('active');
		jQuery('body').addClass('mini-sidebar');
	} else {
		jQuery('.side-bar-width a.maxi').addClass('active').siblings('a').removeClass('active');
		jQuery('body').removeClass('mini-sidebar');
	}
	return themeSettings;
}

function changeColor(color){
	jQuery("#styler_color").remove();
	jQuery('head').append('<style type="text/css" id="styler_color">.styler_border_color, .styler_hover_border_color:hover, .styler_parent:hover > .styler_hover_border_color, .styler_parent_active.active > .styler_active_border_color, .styler_active_itself_border_color.active, .styler_active_itself_border_color.active + .styler_active_next_border_color {border-color:' + color + ' !important;} .styler_color, .styler_hover_color:hover, .styler_parent_active.active > .styler_active_color  {color: ' + color + ' !important;} .styler_bg_color, .styler_hover_bg_color:hover, .styler_parent_active.active > .styler_active_bg_color {background-color: ' + color + ' !important;}</style>');
	jQuery(".styler_infograph").removeClass('visible');
	jQuery(".easy-pie-chart.styler_infograph").data('easyPieChart', '');
	jQuery(".styler_infograph").attr('data-color', color);
	initProgressBarWithImage();
	progress_bars();
	easePieChart();
	processBox();
}

function rgb2hex(rgb) {
	rgb = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
	function hex(x) {
		return ("0" + parseInt(x).toString(16)).slice(-2);
	}
	return "#" + hex(rgb[1]) + hex(rgb[2]) + hex(rgb[3]);
}

function colorSwitcherPosition(){
	var h = jQuery(window).height();
	if(h < jQuery("#mtp-wrapper").height()) {
		jQuery("#mtp-toggle, #mtp-wrapper").addClass('absolute');
	} else {
		jQuery("#mtp-toggle, #mtp-wrapper").removeClass('absolute');
	}
}

function colorPicker(color){
	jQuery('.mtp-color-field').iris({
		palettes: false,
		border: false,
		width: 155,
		color: color,
		mode: 'hsl',
		change: function(event, ui) {
			
			var color = ui.color.toString();
			setThemeSettings('color', color);
			changeColor(color);
			/* Background fix */
			jQuery('.mtp-off .background-block').css( 'background-color', '#f7f7f7');
		}
	});
}


jQuery(window).load(function(){
	jQuery('body').css('visibility', 'visible');	
})

jQuery(window).resize(function(){
	colorSwitcherPosition();
})