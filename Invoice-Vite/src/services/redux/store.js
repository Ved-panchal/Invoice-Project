import { configureStore } from '@reduxjs/toolkit'
import rootReducer from './rootReducer'
import cartReducer from '../redux/reducers/cartReducers'

const store = configureStore({
    reducer: { rootReducer, cart: cartReducer },
})

export { store }
