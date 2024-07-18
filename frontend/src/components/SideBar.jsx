import React, { useState } from 'react'
import { HiMenuAlt3 } from 'react-icons/hi'
import { RiChatHistoryLine } from "react-icons/ri";
import { GrResources } from "react-icons/gr";
import { MdOutlineQuiz } from "react-icons/md";
import { RiProgress3Line } from "react-icons/ri";
import { MdOutlineLogout } from "react-icons/md";
import { MdOutlineChatBubbleOutline } from "react-icons/md";
// import { LuPenSquare } from "react-icons/lu";
import { Link } from 'react-router-dom';
import axios from 'axios';


const SideBar = ({ setSelectedComponent, setSelectedQuizDifficulty }) => {
    const menus = [
        {name:"Chat Bot", key: 'chatbot', icon:MdOutlineChatBubbleOutline},
        // {name:"New Chat", link:"/", icon:LuPenSquare},
        {name:"Past Papers", key: 'pastpapers', icon:GrResources},
        {name:"Quiz", key: 'quiz', icon:MdOutlineQuiz, submenu: [
            { name: 'Easy', key: 'easy' },
            { name: 'Medium', key: 'medium' },
            { name: 'Hard', key: 'hard' },
        ]},
        // {name:"Progress", key: 'progress', icon:RiProgress3Line},    
        // {name:"Log Out", key: 'logout', icon:MdOutlineLogout, margin:true},
    ]

    const [open, setOpen] = useState(false)
    const [submenuOpen, setSubmenuOpen] = useState(false)

    const handleMenuClick = (menu) => {
        if (menu.key === 'quiz') {
            setOpen(true)
            setSubmenuOpen(!submenuOpen)
        }
        else {
            setSelectedComponent(menu.key)
            setSubmenuOpen(false)
        }
        
    }

    const handleSubmenuClick = (submenu) => {
        setSelectedQuizDifficulty(submenu.key)
        setSelectedComponent('quizIntro')
    }
 
  return (
    <div className='bg-[#F5F5F5]'>
            <div className={`bg-[#e6fbfa] h-full ${open? "w-72" : "w-16"} duration-500 text-[#2d3137] px-4`}>
                <div className='py-5 flex justify-end'>
                    <HiMenuAlt3 size={26} className='cursor-pointer' onClick={() => setOpen(!open)} />
                </div>
                <div className='mt-4 flex flex-col gap-4 relative'>
                    {
                        menus?.map((menu, i) => (
                            <div key={i}>
                            
                                <div
                                    onClick={() => handleMenuClick(menu)}
                                    className={`group ${menu.margin && 'mt-5'} flex items-center gap-3.5 font-medium p-2 hover:bg-[#b4f2ef] rounded-md cursor-pointer`}
                                >
                                <div>
                                    {React.createElement(menu.icon, { size: '20' })}
                                </div>
                                <h2 className={`whitespace-pre ${!open && 'opacity-0 overflow-hidden'}`}>{menu.name}</h2>
                                <h2
                                    className={`${open && 'hidden'} absolute whitespace-pre left-48 bg-[#F5F5F5] text-sm font-semibold text-gray-900 rounded-md drop-shadow-lg px-0 py-0 w-0 overflow-hidden group-hover:px-2 group-hover:py-1 group-hover:left-14 group-hover:duration-300 group-hover:w-fit`}
                                >
                                {menu.name}
                                </h2>

                                </div>

                                {
                                    menu.submenu && submenuOpen && (
                                        <div className={`pl-12 ${open ? 'block' : 'hidden'}`}>
                                            {
                                                menu.submenu.map((submenu, j) => (
                                                    <div
                                                    key={j}
                                                    onClick={() => handleSubmenuClick(submenu)}
                                                    className='flex items-center gap-3.5 font-medium p-2 hover:bg-[#b4f2ef] rounded-md cursor-pointer'
                                                    >
                                                        {/* <div className='w-3 h-3 bg-[#2d3137] rounded-full'></div> */}
                                                        <h2 className='whitespace-pre'>{submenu.name}</h2>

                                                    </div>
                                                ))
                                            }
                                        </div>
                                    )
                                }
                        {/* {menu.name === "Chat History" && Array.isArray(chatTitles) && chatTitles.length > 0 && (
                            <div className="ml-4 mt-2">
                                {chatTitles.map((chat, index) => (
                                    <p key={index} className='text-sm text-gray-700 cursor-pointer p-3'>{chat.chat_title}</p>
                                ))}
                            </div>
                        )} */}
                        </div>
                        ))
                    }

                </div>
                
            </div>
            
        
    </div>
  )
}

export default SideBar