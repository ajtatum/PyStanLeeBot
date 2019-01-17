class SlackRequest(object):

    ChannelName=None
    ChannelId=None
    UserName=None
    UserId=None
    Text=None

    def __init__(self, channelName, channelId, userName, userId, text):
        self.ChannelName = channelName
        self.ChannelId = channelId
        self.UserName = userName
        self.UserId = userId
        self.Text = text

    def __init__(self):
        pass