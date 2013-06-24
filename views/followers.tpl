%# list of followings 

% include shared/header.tpl header=page,logged=logged
<div id="main">

	<div class="followers">
	%for follower in followers:
		<p><img src = "/static/feng.jpg" />{{follower.username}}
		<span <a href ="/{{follower.username}}">{{follower.tweet_count}} tweet , following {{ follower.followees_count}} ,follower {{follower.followers_count}} </a></span>
	%end
	</div>
</div>

%include shared/footer.tpl
		
	

