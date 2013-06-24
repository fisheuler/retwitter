%# list of followings 

% include shared/header.tpl header=page,logged=logged
<div id="main">

	<div class="followees">
	%for followee in followees:
		<p><img src = "/static/feng.jpg" />{{followee.username}}
		<span <a href ="/{{followee.username}}">{{followee.tweet_count}} tweet , following {{ followee.followees_count}} ,follower {{followee.followers_count}} </a></span>
	%end
	</div>
</div>

%include shared/footer.tpl
		
	

