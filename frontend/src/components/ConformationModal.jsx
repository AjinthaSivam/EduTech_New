import React from 'react'

const ConformationModal = ({ show, onConfirm, onCancel }) => {
    if (!show) return null
  return (
    <div className='fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center'>
        <div className='bg-white p-6 rounded-lg shadow-lg'>
            <p>Are you sure you want to finish the quiz?</p>
            <div className='flex justify-end mt-4'>
                <button onClick={onCancel} className='px-4 py-2 mr-2 bg-gray-500 text-white rounded-lg'>No</button>
                <button onClick={onConfirm} className='px-4 py-2 bg-[#341db3] text-white rounded-lg'>Yes</button>
            </div>
        </div>

    </div>
  )
}

export default ConformationModal