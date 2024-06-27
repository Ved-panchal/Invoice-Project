// src/services/redux/reducers/index.js

import { combineReducers } from 'redux';
import authReducers from './reducers/authReducers';


const rootReducer = combineReducers({
  auth: authReducers,

});

export default rootReducer;
