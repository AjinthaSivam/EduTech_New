import React, { useEffect, useState, useRef } from 'react'
import axios from 'axios'
import { FiSend } from "react-icons/fi";
import { MdOutlineKeyboardVoice } from "react-icons/md";
import { MdKeyboardVoice } from "react-icons/md";
import { MdArrowUpward } from "react-icons/md";
import { LuPenSquare } from "react-icons/lu";
import { SlOptionsVertical } from "react-icons/sl";
import { CiEraser } from "react-icons/ci";
import { CgSearch } from "react-icons/cg";
import '../styles/custom.css'
import { marked } from 'marked'
import parse from 'html-react-parser';

const Chat = () => {
    const [messages, setMessages] = useState([
        // {   sender: 'bot', 
        //     text: `Hey ${localStorage.getItem('username')}! 😊🌟\n\nReady to embark on an exciting journey of learning English? 📚✨\n\nHow can I assist you today?`,
        //     time: new Date()
        // }
    ])

    const [input, setInput] = useState('')
    const [listening, setListening] = useState(false);
    const [recognition, setRecognition] = useState(null);
    const chatContainerRef = useRef(null);

    useEffect(() => {
        const initialBotMessage = {
            sender: 'bot', 
            text: `Hey ${localStorage.getItem('username')}! 😊🌟\n\nReady to embark on an exciting journey of learning English? 📚✨\n\nHow can I assist you today?`,
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
        getChatHistory();
    }, []);

    useEffect(() => {
        setTimeout(() => {
            scrollToBottom();
        }, 100);
    }, [messages]);

    const scrollToBottom = () => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    };

    

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

    const getChatHistory = async() => {
        try {
            const response = await axios.get('http://127.0.0.1:8000/api/chat/history', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access')}`
                }
            })

            console.log(response.data)

            if (response && response.data) {
                const previousMessages = response.data.flatMap(chat => chat.history.flatMap(entry => ([
                    { sender: 'user', text: entry.message, time: new Date(entry.timestamp) },
                    { sender: 'bot', text: entry.response, time: new Date(entry.timestamp) }
                ])))
                setMessages(prevMessages => [
                    prevMessages[0],
                    ...previousMessages
                ])
            } else {
                console.error('Invalid response format:', response)
            }

        } catch (error) {
            console.error('Error fetching chat history:', error)
        }
    }

    const sendMessage = async (message) => {
        if (message.trim()) {
            const newMessage = { sender: 'user', text: message, time: new Date() };
            setMessages(prevMessages => [...prevMessages, newMessage]);
            setInput('');

            try {
                const response = await axios.post('http://127.0.0.1:8000/chat/', {
                    user_input: message,
                    // new_chat: false
                }, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('access')}`
                    }
                });
                
                if (response && response.data && response.data.response) {
                    const botResponse = response.data.response;
                    

                    const botMessage = { sender: 'bot', text: formatBotResponse(botResponse), time: new Date() };
                    setMessages(prevMessages => [...prevMessages, botMessage]);
                } else {
                    console.error('Invalid response format:', response);
                    // Handle invalid response format here
                }
            } catch (error) {
                console.error('Error sending message:', error);
                // Handle network errors or other exceptions here
            }
        }
    };

    const createNewChat = async () => {
        try {
            const endResponse = await axios.post(
                'http://127.0.0.1:8000/api/end_conversation/', {},
                {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('access')}`
                    }
                }
            )

            if (endResponse && endResponse.data && endResponse.data.success) {
                const initialBotMessage = {
                    sender: 'bot',
                    text: 'Welcom Back!',
                    time: new Date()
                }
                setMessages([initialBotMessage])
            } else {
                console.error('Failed to end the current chat:', endResponse);
                // Handle invalid response format here
            }
        } catch (error) {
            console.error('Error ending the current chat:', error);
            // Handle network errors or other exceptions here
        }
    }

    const handleSend = () => {
        sendMessage(input)
    }

    const formatBotResponse = (response) => {
        // const formattedResponse = response.replace(/\n/g, '<br/>')
        //     .replace(/a\)/g, '<br/><strong>a)</strong>')
        //     .replace(/b\)/g, '<br/><strong>b)</strong>')
        //     .replace(/c\)/g, '<br/><strong>c)</strong>')
        
        // return formattedResponse

        return marked(response)
    }

  return (
    
    <div className='flex flex-col h-full p-4 w-full max-w-4xl mx-auto'>
        <div className='flex justify-end'>
            {/* <button onClick={createNewChat} className='p-2 mt-4 ml-3 text-[#04bdb4] hover:rounded-full hover:bg-[#e6fbfa]'>
                <LuPenSquare size={25} />
            </button> */}
            <button className='p-2 mt-4 ml-3 text-[#04bdb4] hover:rounded-full hover:bg-[#e6fbfa]'>
                <SlOptionsVertical size={20} />
            </button>

        </div>
        
        <div className='flex-grow overflow-auto mt-8 mb-4 px-3 overflow-y-scroll scrollbar-hidden'>
            {
                messages.map((message, index) => (
                    <div key={index} className={`flex mb-2 ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-xs p-2 rounded-lg ${message.sender === 'user' ? 'bg-[#04aaa2] text-[#fbfafb]' : 'bg-[#e6fbfa] text-[#2d3137]'}`}>
                            {message.sender === 'bot' ? (<div className='whitespace-pre-line' dangerouslySetInnerHTML={{__html: message.text}}/>) : (message.text)}
                            
                        </div>
                        <p className='text-xs text-gray-500 ml-2 self-end'>{formatTime(message.time)}</p>

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
        {/* Custom scrollbar div */}
        {/* <div className="chat-scrollbar"> */}
                {/* &nbsp; */}
            {/* </div> */}

    </div>
  )
}

function formatTime(time) {
    return time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit'})
}

export default Chat