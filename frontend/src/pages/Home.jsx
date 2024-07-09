import React from 'react'
import SideBar from '../components/SideBar'
import Chat from '../components/Chat'
import NavBar from '../components/NavBar'

const Home = () => {
  return (
    <div className='bg-white'>
      <NavBar />
      <section className='h-screen flex pt-16'>
        <SideBar />
        <Chat />
      </section>
        
    </div>
    
  )
}

export default Home