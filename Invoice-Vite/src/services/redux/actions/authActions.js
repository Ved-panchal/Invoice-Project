// src/services/redux/actions/authActions.js
import { loginSuccess, loginFailure } from '../reducers/authReducers'
import config from '../../config';
import { showToast } from '../../toasts/index'

export const loginUser = (credentials) => async (dispatch) => {
    try {
        const response = await fetch(`${config.API_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(credentials),
        });

        console.log('Response:', response);

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        const authToken = data.token;
        document.cookie = `authToken=${authToken}; path=/`;

        dispatch(loginSuccess(data.userInfo));
        showToast(data.msg, 'success');
    } catch (error) {
        console.error('Fetch Error:', error);
        dispatch(loginFailure('Login failed. Please try again.'));
        showToast('Login failed. Please try again.', 'error');
    }
};

