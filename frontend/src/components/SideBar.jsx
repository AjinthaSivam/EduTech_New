import React, { useState } from 'react'
import { HiMenuAlt3 } from 'react-icons/hi'
import { RiChatHistoryLine } from "react-icons/ri";
import { GrResources } from "react-icons/gr";
import { MdOutlineQuiz } from "react-icons/md";
import { RiProgress3Line } from "react-icons/ri";
import { MdOutlineLogout } from "react-icons/md";
// import { LuPenSquare } from "react-icons/lu";
import { Link } from 'react-router-dom';
import axios from 'axios';


const SideBar = () => {
    const menus = [
        {name:"Chat History", link:"#", icon:RiChatHistoryLine},
        // {name:"New Chat", link:"/", icon:LuPenSquare},
        {name:"Reference", link:"/", icon:GrResources},
        {name:"Quiz", link:"/", icon:MdOutlineQuiz},
        {name:"Progress", link:"/", icon:RiProgress3Line},    
        {name:"Log Out", link:"/", icon:MdOutlineLogout, margin:true},
    ]

    const [open, setOpen] = useState(false)
    const [chatTitles, setChatTitles] = useState([])

    const getChatTitles = async () => {
        try {
            console.log("getting chat titles...");
            const response = await axios.get('/api/chat/history', {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem('access')}`
                }
            })
            console.log("Response data:", response.data);
            setChatTitles(response.data)
        } catch (error) {
            console.error("Error getting chat titles:", error)
        }
    }

    const handleMenuClick = (menu) => {
        if (menu.name === "Chat History") {
            getChatTitles()
        }
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
                            
                        <Link 
                            to={menu?.link} 
                            onClick={() => handleMenuClick(menu)}
                            
                            className={`group ${menu?.margin && 'mt-5'} flex items-center gap-3.5 font-medium p-2 hover:bg-[#b4f2ef] rounded-md` }
                        >
                                <div>{ React.createElement( menu?.icon, { size: "20" }) }</div>
                                <h2 className={`whitespace-pre ${!open && 'opacity-0 overflow-hidden'}`}>{menu?.name}</h2>
                                
                                <h2
                                    className={`${open && "hidden"} absolute whitespace-pre left-48 bg-[#F5F5F5] text-sm font-semibold text-gray-900 rounded-md drop-shadow-lg px-0 py-0 w-0 overflow-hidden group-hover:px-2 group-hover:py-1 group-hover:left-14 group-hover:duration-300 group-hover:w-fit`}
                                >
                                    {menu.name}
                                </h2>
                
                        </Link>
                        {menu.name === "Chat History" && Array.isArray(chatTitles) && chatTitles.length > 0 && (
                            <div className="ml-4 mt-2">
                                {chatTitles.map((chat, index) => (
                                    <p key={index} className='text-sm text-gray-700 cursor-pointer p-3'>{chat.chat_title}</p>
                                ))}
                            </div>
                        )}
                        </div>
                        ))
                    }

                </div>
                
            </div>
            
        
    </div>
  )
}

export default SideBar