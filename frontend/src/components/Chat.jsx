import React, { useEffect, useState, useRef } from 'react'
import axios from 'axios'
import { MdOutlineKeyboardVoice } from "react-icons/md";
import { MdKeyboardVoice } from "react-icons/md";
import { MdArrowUpward } from "react-icons/md";
import { FaEraser } from "react-icons/fa";
import { CgSearch } from "react-icons/cg";
import '../styles/custom.css'
import { marked } from 'marked'
import BotLogo from '../images/bot.png'

const Chat = () => {
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState('')
    const [listening, setListening] = useState(false);
    const [recognition, setRecognition] = useState(null);
    const chatContainerRef = useRef(null);
    const [chatId, setChatId] = useState(null);

    useEffect(() => {
        const initialBotMessage = {
            sender: 'bot', 
            text: `Hey ${localStorage.getItem('username')}! 😊🌟\n\nWelcome to EduTech Teaching Assistant! \n\n`,
            time: new Date()
        }
        setMessages([initialBotMessage])
    
        
        // Initialize Webkit Speech Recognition
        if ('webkitSpeechRecognition' in window) {
            const recognition = new window.webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onstart = () => setListening(true);
            recognition.onend = () => setListening(false);
            recognition.onerror = (event) => console.error(event.error);
            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                setInput(transcript);
                sendMessage(transcript);
            };

            setRecognition(recognition);
        } else {
            console.warn('Webkit Speech Recognition is not supported in this browser.');
        }
        // getChatHistory();
    }, []);
    

    const startVoiceRecognition = () => {
        if (recognition) {
            recognition.start();
        }
    };

    const stopVoiceRecognition = () => {
        if (recognition) {
            recognition.stop();
        }
    };

    const getChatHistory = async () => {
        try {
            const response = await axios.get('http://127.0.0.1:8000/api/chat/history', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access')}`
                }
            });
    
            if (response && response.data) {
                // console.log('Chat history response:', response.data);
    
                const previousMessages = response.data.flatMap(chat => chat.history.flatMap(entry => ([
                    { sender: 'user', text: chat.message, time: new Date(entry.timestamp) },
                    { sender: 'bot', text: chat.response, time: new Date(entry.timestamp) }
                ])));
                
                setMessages(prevMessages => [
                    prevMessages[0], // Keeping the initial bot message
                    ...previousMessages
                ]);
            } else {
                console.error('Invalid response format:', response);
            }
    
        } catch (error) {
            console.error('Error fetching chat history:', error);
        }
    };
    

    const sendMessage = async (message) => {
        if (message.trim()) {
            const newMessage = { sender: 'user', text: message, time: new Date() };
            setMessages(prevMessages => [...prevMessages, newMessage]);
            setInput('');

            try {
                const response = await axios.post('http://127.0.0.1:8000/api/chat/', {
                    user_input: message,
                    new_chat: chatId === null,
                    chat_id: chatId
                }, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('access')}`
                    }
                });

                if (response && response.data && response.data.response) {
                    const botResponse = response.data.response;

                    const botMessage = { sender: 'bot', text: formatBotResponse(botResponse), time: new Date() };
                    setMessages(prevMessages => [...prevMessages, botMessage]);

                    if (chatId === null) {
                        setChatId(response.data.chat_id);
                    }
                } else {
                    console.error('Invalid response format:', response);
                }
            } catch (error) {
                console.error('Error sending message:', error);
            }
        }
    };

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const scrollToBottom = () => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
        }
    }

    const handleSend = () => {
        sendMessage(input)
    }

    const formatBotResponse = (response) => {
        return marked(response)
    }

  return (
    
    <div className='flex flex-col h-full p-6 w-full max-w-5xl mx-auto'>
        <div className='flex justify-end'>
        </div>
        
        <div className='flex-grow overflow-auto mt-8 mb-4 px-3' ref={chatContainerRef}>
            {
                messages.map((message, index) => (
                    <div key={index} className={`flex mt-4 mb-4 ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`relative max-w-3xl p-4 rounded-lg ${message.sender === 'user' ? 'bg-[#04aaa2] text-[#fbfafb]' : 'bg-[#e6fbfa] text-[#2d3137]'}`}>
                            {
                                message.sender === 'bot' && (
                                    <img src={BotLogo} alt="Bot Logo" className="absolute left-2 -top-5 h-8 w-8" />
                                )
                            }
                            {message.sender === 'bot' ? (<div className='whitespace-pre-line' dangerouslySetInnerHTML={{__html: message.text}}/>) : (message.text)}
                            <p className={`absolute bottom-1 right-2 text-xs ${message.sender === 'user' ? 'text-gray-300' : 'text-gray-500'}`}>{formatTime(message.time)}</p>
                        </div>
                        

                    </div>
                ))
            }
        </div>
        <div className='flex px-3'>
            <button onClick={listening? stopVoiceRecognition : startVoiceRecognition} className='p-2 text-[#04aaa2] rounded-full mr-2 hover:bg-[#e6fbfa]'>
                {listening? <MdKeyboardVoice size={30}/> : <MdOutlineKeyboardVoice size={25}/>}
            </button>
            <input 
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                className='flex-grow p-2 pl-4 border rounded-full focus:outline-none' 
                placeholder='Type your message...'
            />
            
            <button onClick={handleSend} className='p-2 bg-[#04aaa2] text-[#fbfafb] rounded-full ml-2 hover:bg-[#04bdb4]'>
                <MdArrowUpward size={25}/>
            </button>

        </div>
    </div>
  )
}

function formatTime(time) {
    return time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit'})
}

export default Chat