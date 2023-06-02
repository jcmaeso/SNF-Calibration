function  Pmn  = Pmn( m,n,x )
%computes the associated Legendre function of degree n and order m at 
%point (x)
if m>n
    Pmn=0*x;
else
    N = legendre2(n,x,'norm');
    Pmn=permute(N(m+1,:,:),[2 3 1]);
end



end

