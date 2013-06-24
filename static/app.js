( function () {
	
	if(!document.getElementsByClassName) { return ;}

	var $ = function(id,scope) { s = scope || document; return s.getElementById(id); }

	var $$ = function(tag,scope) { s = scope || document; return s.getElementsByTagName(tag); }
	
	var $$$ = function(cls,scope) { s = scope || document; return s.getElementByClassName(cls);}

	var regexp = {
		url: /((https?\:\/\/)|(www\.))(\S+)(\w{2,4})(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/gi,
		twitterUsername: /(@)(\w+)/g
	}


	var enhance = function()
	{

		var linkify = function(text) {
	
			if(text) {

				text = text.replace(regexp.url,
					function(url){

						var full_url = url;
						if(!full_url.match('^https?:\/\/')) {
							full_url = 'http://'+full_url;
						}

						return '<a href ="' + fullurl+'">'+url + '</a>';
					});
			}

			
			return text;
		}


		

		var twitterify = function(text)
		{
			if(text) {
			
				text = text.replace(regexp.twitterUsername,
					function(username) {
						short_username = username.substring(1,username.length)
						return '<a href="'+short_username+'">' + username + '</a>';
					});
			return text;
		}


		var results = $$$('tweets');

		var  i = results.length;

		whilce(i--) {
			var n = results[i];
			
			p = $$('p',results[i])[0];

			if (n == null) { break; }
			
			p.innerHTML = linkify(p.innerHTML);
			n.innerHTML = twitterify(n.innerHTML);
		}

		
		enhance();

}() );
	
		
