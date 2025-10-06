<template>
    <li class="cart-nav onhover-dropdown">
        <div class="cart-box">
            <svg>
                <use href="@/assets/svg/icon-sprite.svg#Buy"></use>
            </svg>
        </div>
        <div class="cart-dropdown onhover-show-div">
            <h6 class="f-18 mb-0 dropdown-title">Cart</h6>
            <ul>
                <li>
                    <div class="d-flex"><img class="img-fluid b-r-5 img-60" src="@/assets/images/ecommerce/05.jpg" alt="">
                        <div class="flex-grow-1"><span>Women's Track Suit</span>
                            <div class="qty-box">
                                <div class="input-group"><span class="input-group-prepend">
                                        <button class="btn quantity-left-minus" type="button" data-type="minus"
                                            data-field="">-</button></span>
                                    <input class="form-control input-number" type="text" name="quantity" value="1"><span
                                        class="input-group-prepend">
                                        <button class="btn quantity-right-plus" type="button" data-type="plus"
                                            data-field="">+</button></span>
                                </div>
                            </div>
                            <h6 class="font-primary">$500</h6>
                        </div>
                        <div class="close-circle"><a class="bg-danger" href="#"><i data-feather="x"></i></a></div>
                    </div>
                </li>
                <li>
                    <div class="d-flex"><img class="img-fluid b-r-5 img-60" src="@/assets/images/ecommerce/02.jpg" alt="">
                        <div class="flex-grow-1"><span>Men's Jacket</span>
                            <div class="qty-box">
                                <div class="input-group"><span class="input-group-prepend">
                                        <button class="btn quantity-left-minus" type="button" data-type="minus"
                                            data-field="">-</button></span>
                                    <input class="form-control input-number" type="text" name="quantity" value="1"><span
                                        class="input-group-prepend">
                                        <button class="btn quantity-right-plus" type="button" data-type="plus"
                                            data-field="">+</button></span>
                                </div>
                            </div>
                            <h6 class="font-primary">$500.00</h6>
                        </div>
                        <div class="close-circle"><a class="bg-danger" href="#"><i data-feather="x"></i></a></div>
                    </div>
                </li>
                <li class="total">
                    <h6 class="mb-0">Order Total : <span class="f-right">$1000.00</span></h6>
                </li>
                <li class="text-center"><a class="d-block mb-3 view-cart f-w-700" href="cart.html">Go to your cart</a><a
                    class="btn btn-primary view-checkout" href="checkout.html">Checkout </a></li>
        </ul>
    </div>
</li></template>
