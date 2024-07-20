import React, { useState } from 'react'
import SideBar from './SideBar'
import Chat from './Chat'
import MCQGenerator from './Quiz'
import QuizIntro from './QuizIntro'
import PastPaper from './PastPaper'

const Main = () => {
    const [selectedComponent, setSelectedComponent] = useState('chatbot')
    const [selectedQuizDifficulty, setSelectedQuizDifficulty] = useState('')


    const handleStartQuiz = () => {
      setSelectedComponent('quiz')
    }

    const renderComponent = () => {
        switch (selectedComponent) {
            case 'chatbot':
              return <Chat />
            case 'quizIntro':
              return <QuizIntro difficulty={selectedQuizDifficulty} onStartQuiz={handleStartQuiz}/>
            case 'quiz':
              return <MCQGenerator difficulty={selectedQuizDifficulty} setSelectedComponent={setSelectedComponent}/> 
            case 'pastpapers':
              return <PastPaper />  
            default:
              return <Chat />
        }
    }
  return (
    <div>
        <section className='h-screen flex pt-16'>
        <SideBar setSelectedComponent={setSelectedComponent} setSelectedQuizDifficulty={setSelectedQuizDifficulty} />
        {renderComponent()}
      </section>
    </div>
  )
}

export default Main