%# single post template
%include shared/header.tpl header=page,logged=logged
<div class="tweets">
	<p><img src="/statc/feng.png" /> <strong><a href="/{{tweet.user.username}}">{{tweet.user.username}}</a></strong>{{tweet.content}}<span><a href="/{{username}}/statuses/{{tweet.id}}">permaink</a></span></p>
</div>

%include shared/footer.tpl



