import { createSlice } from '@reduxjs/toolkit'
import {
    addItemToCart,
    emptyCart,
    fetchCart,
    removeItemFromCart,
} from '../actions/cartAction'

const cartSlice = createSlice({
    name: 'cart',
    initialState: {
        items: [],
        status: 'idle',
        error: null,
    },
    reducers: {
        updateQuantity: (state, action) => {
            const { productId, quantity } = action.payload
            const itemIndex = state.items.findIndex(
                (item) => item.id === productId
            )
            if (itemIndex !== -1) {
                state.items[itemIndex].quantity = quantity
            }
        },
        removeItem: (state, action) => {
            const { productId } = action.payload
            state.items = state.items.filter((item) => item.id !== productId)
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(addItemToCart.pending, (state) => {
                state.status = 'loading'
            })
            .addCase(addItemToCart.fulfilled, (state, action) => {
                state.status = 'succeeded'
                const existingProduct = state.items.find(
                    (item) => item.id === action.payload.product_id
                )
                if (existingProduct) {
                    existingProduct.quantity += action.payload.quantity
                } else {
                    state.items.push(action.payload)
                }
            })
            .addCase(addItemToCart.rejected, (state, action) => {
                state.status = 'failed'
                state.error = action.error.message
            })
            .addCase(fetchCart.pending, (state) => {
                state.status = 'loading'
            })
            .addCase(fetchCart.fulfilled, (state, action) => {
                state.status = 'succeeded'
                state.items = action.payload.products
            })
            .addCase(fetchCart.rejected, (state, action) => {
                state.status = 'failed'
                state.error = action.error.message
            })
            .addCase(removeItemFromCart.pending, (state) => {
                state.status = 'loading'
            })
            .addCase(removeItemFromCart.fulfilled, (state, action) => {
                state.status = 'succeeded'
                const { productId } = action.payload
                state.items = state.items.filter(
                    (item) => item.id !== productId
                )
            })
            .addCase(removeItemFromCart.rejected, (state, action) => {
                state.status = 'failed'
                state.error = action.error.message
            })
            .addCase(emptyCart.pending, (state) => {
                state.status = 'loading';
              })
              .addCase(emptyCart.fulfilled, (state) => {
                state.status = 'succeeded';
                state.items = [];
              })
              .addCase(emptyCart.rejected, (state, action) => {
                state.status = 'failed';
                state.error = action.error.message;
              });
    },
})

export const { updateQuantity, removeItem } = cartSlice.actions

export default cartSlice.reducer
