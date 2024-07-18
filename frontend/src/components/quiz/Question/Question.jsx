import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Typography } from '@mui/material';

const Question = () => {
    const navigate = useNavigate();

    const goToNextQuestion = () => {
        navigate('/next-question');
    };

    return (
        <div>
            <Typography variant="h4">Question</Typography>
            <Button onClick={goToNextQuestion}>Next Question</Button>
        </div>
    );
};

export default Question;
