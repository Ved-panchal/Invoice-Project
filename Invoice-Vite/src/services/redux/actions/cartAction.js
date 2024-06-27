import { createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';
import config from '../../config';

const axiosInstance = axios.create({
  baseURL: config.API_URL,
  withCredentials: true,
});

export const addItemToCart = createAsyncThunk(
  'cart/addItemToCart',
  async ({ userId, product, quantity }) => {
    const response = await axiosInstance.post(`/cart/${userId}`, {
      product_id: product.id,
      quantity: quantity ? quantity : 1,
    });
    return response.data;
  }
);

export const fetchCart = createAsyncThunk(
  'cart/fetchCart',
  async (userId, { getState }) => {
    const response = await axiosInstance.get(`/cart/${userId}`);

    const products = response.data.products.map((product) => ({
      productId: product.product_id,
      quantity: product.quantity,
    }));

    const apiCalls = products.map(async (product) => {
      const productResponse = await fetch(`${config.API_URL}/getproduct/${product.productId}`);
      const productData = await productResponse.json();
      return { ...productData, quantity: product.quantity };
    });

    const productData = await Promise.all(apiCalls);

    const combinedData = {
      ...response.data,
      products: productData,
    };
    
    return combinedData;
  }
);

export const removeItemFromCart = createAsyncThunk(
  'cart/removeItemFromCart',
  async ({ userId, productId }) => {
    const response = await axiosInstance.delete(`/cart/${userId}`, {
      data: { product_id: productId },
    });
    return response.data;
  }
);

export const updateQuantity = createAsyncThunk(
  'cart/updateQuantity',
  async ({ userId, productId, quantity }) => {
    try {
      const response = await axiosInstance.put(`/cart/${userId}`, {
        product_id: productId,
        quantity,
      });

      return response.data;
    } catch (error) {
      console.error('Error updating quantity:', error);
      throw error;
    }
  }
);

export const emptyCart = createAsyncThunk(
  'cart/emptyCart',
  async (userId) => {
    const response = await axiosInstance.delete(`/cart/${userId}/empty`);
    return response.data;
  }
);
