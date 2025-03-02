import React, { useState, useEffect, useRef } from 'react';
import { Box, Paper, TextField, Button, Typography, Avatar, CircularProgress } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import MicIcon from '@mui/icons-material/Mic';
import ReactMarkdown from 'react-markdown';
import { useQuery, useMutation } from 'react-query';
import { sendMessage, getConversationHistory } from '../../api/chatApi';
import FileUploader from '../common/FileUploader';
import AudioRecorder from '../common/AudioRecorder';

const MessageItem = ({ message, isUser }) => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: isUser ? 'row-reverse' : 'row',
        mb: 2,
        gap: 1,
      }}
    >
      <Avatar
        sx={{
          bgcolor: isUser ? 'primary.main' : 'secondary.main',
        }}
      >
        {isUser ? 'U' : message.agent_name ? message.agent_name[0] : 'A'}
      </Avatar>
      <Paper
        elevation={1}
        sx={{
          p: 2,
          maxWidth: '80%',
          bgcolor: isUser ? 'primary.light' : 'background.paper',
          borderRadius: 2,
        }}
      >
        {message.thinking && !isUser && (
          <Box sx={{ mb: 1, p: 1, bgcolor: 'grey.100', borderRadius: 1 }}>
            <Typography variant="caption" color="textSecondary">
              Agent thinking:
            </Typography>
            <Typography variant="body2" sx={{ fontStyle: 'italic', whiteSpace: 'pre-wrap' }}>
              {message.thinking}
            </Typography>
          </Box>
        )}
        <Typography variant="body1">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </Typography>
        {message.sources && message.sources.length > 0 && (
          <Box sx={{ mt: 1 }}>
            <Typography variant="caption" color="textSecondary">
              Sources:
            </Typography>
            <ul style={{ margin: '4px 0', paddingLeft: 20 }}>
              {message.sources.map((source, idx) => (
                <li key={idx}>
                  <Typography variant="caption">{source.title || source.id}</Typography>
                </li>
              ))}
            </ul>
          </Box>
        )}
        <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mt: 1 }}>
          {new Date(message.timestamp).toLocaleTimeString()}
          {!isUser && message.agent_name && ` • ${message.agent_name}`}
        </Typography>
      </Paper>
    </Box>
  );
};

const ChatInterface = ({ conversationId }) => {
  const [message, setMessage] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef(null);

  // Get conversation history
  const { data: history, isLoading, refetch } = useQuery(
    ['conversationHistory', conversationId],
    () => getConversationHistory(conversationId),
    {
      enabled: !!conversationId,
      refetchInterval: 3000, // Poll for updates every 3 seconds
    }
  );

  // Send message mutation
  const { mutate, isLoading: isSending } = useMutation(sendMessage, {
    onSuccess: () => {
      setMessage('');
      refetch();
    },
  });

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  const handleSendMessage = () => {
    if (message.trim()) {
      mutate({
        conversationId,
        message: {
          content: message,
          role: 'user',
        },
      });
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileUpload = (file) => {
    setIsUploading(true);
    // Handle file upload logic with API
    console.log('File uploaded:', file);
    setIsUploading(false);
  };

  const handleAudioRecording = (audioBlob) => {
    setIsRecording(false);
    // Handle audio recording logic with API
    console.log('Audio recorded:', audioBlob);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <CircularProgress />
          </Box>
        ) : history && history.messages ? (
          history.messages.map((msg, index) => (
            <MessageItem
              key={index}
              message={msg}
              isUser={msg.role === 'user'}
            />
          ))
        ) : (
          <Typography variant="body1" sx={{ textAlign: 'center', mt: 4, color: 'text.secondary' }}>
            Start a conversation with our agents
          </Typography>
        )}
        <div ref={messagesEndRef} />
      </Box>

      <Paper
        elevation={3}
        sx={{
          p: 2,
          borderTop: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<AttachFileIcon />}
            onClick={() => document.getElementById('file-upload').click()}
            disabled={isSending || isUploading}
          >
            Attach
          </Button>
          <Button
            variant="outlined"
            startIcon={<MicIcon />}
            onClick={() => setIsRecording(!isRecording)}
            color={isRecording ? 'secondary' : 'primary'}
            disabled={isSending || isUploading}
          >
            {isRecording ? 'Stop' : 'Record'}
          </Button>
          <FileUploader id="file-upload" onFileUpload={handleFileUpload} />
          {isRecording && <AudioRecorder onRecordingComplete={handleAudioRecording} />}
        </Box>

        <Box sx={{ display: 'flex', mt: 2, gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            variant="outlined"
            placeholder="Type your message..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isSending || isUploading || isRecording}
          />
          <Button
            variant="contained"
            endIcon={<SendIcon />}
            onClick={handleSendMessage}
            disabled={!message.trim() || isSending || isUploading || isRecording}
          >
            Send
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default ChatInterface; 